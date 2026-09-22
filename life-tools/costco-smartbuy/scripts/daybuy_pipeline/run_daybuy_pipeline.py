#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Pipeline Orchestrator for Daybuy Store Tag Price Verification
Strictly compliant with AGENTS.md (v1.1)

Supports:
  --reset / --clean: Wipe all workspace artifacts and restart from scratch
  --force: Re-run and overwrite output even if SUCCESS checkpoint exists
  --step <step_name>: Run a single step in isolation
  --from-step <step_name>: Invalidate checkpoints from target step onward
  --dry-run: Display step sequence and checkpoint status without running
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
from datetime import datetime, timezone

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(PIPELINE_DIR))
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, ".agent_workspace", "daybuy_price_verification")
STATE_FILE = os.path.join(WORKSPACE_DIR, "state.json")
REPORT_FILE = os.path.join(WORKSPACE_DIR, "report.md")

STEPS = [
    {
        "id": "step_01_filter_target_skus",
        "script": "step_01_filter_target_skus.py",
        "output": os.path.join(WORKSPACE_DIR, "target_skus_manifest.json"),
        "args": lambda s, p: [
            "--output", s["output"],
            "--db", os.path.join(p, "costco_products.db")
        ]
    },
    {
        "id": "step_02_search_daybuy_posts",
        "script": "step_02_search_daybuy_posts.py",
        "input": os.path.join(WORKSPACE_DIR, "target_skus_manifest.json"),
        "output": os.path.join(WORKSPACE_DIR, "daybuy_scraped_results.json"),
        "args": lambda s, p: [
            "--input", s["input"],
            "--output", s["output"]
        ]
    },
    {
        "id": "step_03_download_and_enrich",
        "script": "step_03_download_and_enrich.py",
        "input": os.path.join(WORKSPACE_DIR, "daybuy_scraped_results.json"),
        "output": os.path.join(WORKSPACE_DIR, "verified_products_update.json"),
        "args": lambda s, p: [
            "--input", s["input"],
            "--output", s["output"],
            "--public-img-dir", os.path.join(p, "public", "images", "products")
        ]
    },
    {
        "id": "step_04_apply_db_and_sync",
        "script": "step_04_apply_db_and_sync.py",
        "input": os.path.join(WORKSPACE_DIR, "verified_products_update.json"),
        "output": os.path.join(PROJECT_ROOT, "public", "data", "products.json"),
        "args": lambda s, p: [
            "--input", s["input"],
            "--db", os.path.join(p, "costco_products.db"),
            "--public-json", os.path.join(p, "public", "data", "products.json"),
            "--src-json", os.path.join(p, "src", "data", "products.json")
        ]
    }
]

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(state):
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def generate_report(state, overall_status, durations):
    table_rows = []
    errors = []
    warnings = []

    for s in STEPS:
        sid = s["id"]
        entry = state.get(sid, {})
        status = entry.get("status", "NOT_RUN")
        dur = durations.get(sid, "-")
        out = entry.get("output_path") or s.get("output", "-")
        table_rows.append(f"| `{sid}` | **{status}** | {dur} | `{os.path.basename(out)}` |")
        if entry.get("error"):
            errors.append(f"- **{sid}**: {entry['error'].get('message')}")

    # Read verified products if exists
    verified_file = os.path.join(WORKSPACE_DIR, "verified_products_update.json")
    verified_stats = ""
    if os.path.exists(verified_file):
        try:
            with open(verified_file, "r", encoding="utf-8") as f:
                v_data = json.load(f)
                v_count = v_data.get("total_verified", 0)
                img_count = v_data.get("photos_downloaded", 0)
                verified_stats = f"\n### Daybuy Verification Highlights\n- **Total Products Verified with Store Tag Prices**: {v_count}\n- **Store Price Tag Photos Downloaded**: {img_count}\n\n#### Sample Verified Products:\n"
                for u in v_data.get("verified_updates", [])[:8]:
                    verified_stats += f"- **#{u['sku']}**: {u['name']} -> **NT$ {u['verifiedPrice']}** ({u['verifiedSource']})\n"
        except Exception:
            pass

    report_content = f"""# Execution Report — Daybuy Price Tag Verification Pipeline

## Summary
{overall_status}
{verified_stats}
## Step Status
| Step | Status | Duration | Output |
|------|--------|----------|--------|
{chr(10).join(table_rows)}

## Warnings
{"None" if not warnings else chr(10).join(warnings)}

## Errors
{"None" if not errors else chr(10).join(errors)}

## Next Actions
{"All verification steps completed successfully. Guessed prices have been replaced with real store tag prices and photos in DB and UI." if not errors else "Inspect error logs, patch step scripts, and resume with --from-step."}
"""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\n[REPORT] Execution report generated at: {REPORT_FILE}")

def main():
    parser = argparse.ArgumentParser(description="Daybuy Pipeline Orchestrator")
    parser.add_argument("--reset", "--clean", action="store_true", help="Wipe workspace and reset state")
    parser.add_argument("--force", action="store_true", help="Force re-run steps regardless of checkpoints")
    parser.add_argument("--step", help="Run a specific step in isolation")
    parser.add_argument("--from-step", help="Invalidate checkpoints from step onward and re-run")
    parser.add_argument("--dry-run", action="store_true", help="Print plan and checkpoints without running")
    args = parser.parse_args()

    print("================================================================")
    print("    Costco Daybuy Store Tag Verification Pipeline Runner       ")
    print("================================================================")
    print(f"Project Root:  {PROJECT_ROOT}")
    print(f"Workspace Dir: {WORKSPACE_DIR}")

    if args.reset:
        confirm = input("Are you sure you want to reset workspace? (y/N): ").strip().lower()
        if confirm == 'y':
            if os.path.exists(WORKSPACE_DIR):
                shutil.rmtree(WORKSPACE_DIR)
                print(f"[RESET] Cleared workspace: {WORKSPACE_DIR}")
        return 0

    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    state = load_state()

    step_ids = [s["id"] for s in STEPS]

    if args.dry_run:
        print("\n[DRY RUN] Pipeline Dependency Plan:")
        for idx, s in enumerate(STEPS):
            sid = s["id"]
            c_status = state.get(sid, {}).get("status", "PENDING")
            print(f"  {idx + 1}. {sid:30s} -> Status: [{c_status}]")
        return 0

    target_steps = list(STEPS)

    if args.step:
        if args.step not in step_ids:
            print(f"[ERROR] Step '{args.step}' not found. Available steps: {step_ids}")
            return 1
        target_steps = [s for s in STEPS if s["id"] == args.step]

    elif args.from_step:
        if args.from_step not in step_ids:
            print(f"[ERROR] Step '{args.from_step}' not found. Available steps: {step_ids}")
            return 1
        idx = step_ids.index(args.from_step)
        for invalid_s in STEPS[idx:]:
            sid = invalid_s["id"]
            if sid in state:
                state[sid]["status"] = "PENDING"
        save_state(state)
        target_steps = STEPS[idx:]

    durations = {}
    halted_step = None

    for s in target_steps:
        sid = s["id"]
        step_script = os.path.join(PIPELINE_DIR, s["script"])
        output_file = s["output"]

        # Smart Skip
        is_already_done = (
            state.get(sid, {}).get("status") == "SUCCESS"
            and os.path.exists(output_file)
            and not args.force
        )

        if is_already_done:
            print(f"\n[SKIP] Step '{sid}' already SUCCESS and output exists: {output_file}")
            continue

        if "input" in s and not os.path.exists(s["input"]):
            print(f"\n[FAIL-FAST] Step '{sid}' prerequisite missing: {s['input']}")
            halted_step = sid
            break

        print(f"\n>>> Running: {sid} ({s['script']}) <<<")
        start_ts = datetime.now(timezone.utc).isoformat()
        t0 = time.time()

        state[sid] = {
            "step_name": sid,
            "status": "RUNNING",
            "started_at": start_ts,
            "finished_at": None,
            "output_path": output_file,
            "attempt": state.get(sid, {}).get("attempt", 0) + 1,
            "error": None
        }
        save_state(state)

        cmd = [sys.executable, step_script] + s["args"](s, PROJECT_ROOT)
        if args.force:
            cmd.append("--force")

        res = subprocess.run(cmd, cwd=PROJECT_ROOT)
        dur = f"{time.time() - t0:.2f}s"
        durations[sid] = dur
        end_ts = datetime.now(timezone.utc).isoformat()

        if res.returncode == 0 and os.path.exists(output_file):
            state[sid]["status"] = "SUCCESS"
            state[sid]["finished_at"] = end_ts
            save_state(state)
            print(f"[OK] {sid} finished in {dur}.")
        else:
            state[sid]["status"] = "FAILED"
            state[sid]["finished_at"] = end_ts
            state[sid]["error"] = {
                "type": "ProcessReturnCodeError",
                "message": f"Script {s['script']} exited with code {res.returncode}",
                "traceback": None
            }
            save_state(state)
            print(f"[ERROR] {sid} failed after {dur}!")
            halted_step = sid
            break

    if halted_step:
        overall_status = f"Halted at step: `{halted_step}`"
    else:
        overall_status = f"All {len(target_steps)} Daybuy verification steps succeeded."

    generate_report(state, overall_status, durations)
    return 0 if not halted_step else 1

if __name__ == "__main__":
    sys.exit(main())
