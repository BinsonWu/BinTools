#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Pipeline Orchestrator for Costco Warehouse-Only & Uber Eats Products Ingestion
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
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, ".agent_workspace", "warehouse_products")
STATE_FILE = os.path.join(WORKSPACE_DIR, "state.json")
REPORT_FILE = os.path.join(WORKSPACE_DIR, "report.md")

STEPS = [
    {
        "id": "step_01_crawl_warehouse_products",
        "script": "step_01_crawl_warehouse_products.py",
        "output": os.path.join(WORKSPACE_DIR, "raw_warehouse_products.json"),
        "args": lambda s, p: [
            "--output", s["output"]
        ]
    },
    {
        "id": "step_02_match_daybuy_store_prices",
        "script": "step_02_match_daybuy_store_prices.py",
        "input": os.path.join(WORKSPACE_DIR, "raw_warehouse_products.json"),
        "output": os.path.join(WORKSPACE_DIR, "daybuy_store_prices.json"),
        "args": lambda s, p: [
            "--input", s["input"],
            "--output", s["output"]
        ]
    },
    {
        "id": "step_03_enrich_weights_and_ppu",
        "script": "step_03_enrich_weights_and_ppu.py",
        "input_raw": os.path.join(WORKSPACE_DIR, "raw_warehouse_products.json"),
        "input_daybuy": os.path.join(WORKSPACE_DIR, "daybuy_store_prices.json"),
        "output": os.path.join(WORKSPACE_DIR, "enriched_warehouse_products.json"),
        "args": lambda s, p: [
            "--raw-products", s["input_raw"],
            "--daybuy-prices", s["input_daybuy"],
            "--output", s["output"]
        ]
    },
    {
        "id": "step_04_upsert_db_and_sync",
        "script": "step_04_upsert_db_and_sync.py",
        "input": os.path.join(WORKSPACE_DIR, "enriched_warehouse_products.json"),
        "output": os.path.join(PROJECT_ROOT, "public", "data", "products.json"),
        "args": lambda s, p: [
            "--input", s["input"],
            "--db", os.path.join(p, "costco_products.db"),
            "--frontend-public", os.path.join(p, "public", "data", "products.json"),
            "--frontend-src", os.path.join(p, "src", "data", "products.json"),
            "--report", REPORT_FILE
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

    for step in STEPS:
        sid = step["id"]
        info = state.get(sid, {})
        status = info.get("status", "NOT_RUN")
        dur = durations.get(sid, 0.0)
        dur_str = f"{dur:.2f}s" if dur > 0 else "-"
        out_path = info.get("output_path", step["output"])
        rel_out = os.path.relpath(out_path, PROJECT_ROOT) if out_path else "-"
        
        status_badge = f"**{status}**" if status == "SUCCESS" else status
        table_rows.append(f"| `{sid}` | {status_badge} | {dur_str} | `{rel_out}` |")
        
        if status == "FAILED" and info.get("error"):
            errors.append(f"- **{sid}**: {info['error'].get('message', 'Unknown error')}")

    report_lines = [
        "# Execution Report — Warehouse-Only & Uber Eats Food Pipeline",
        "",
        "## Summary",
        f"{overall_status}",
        "",
        "## Step Status",
        "| Step | Status | Duration | Output |",
        "|------|--------|----------|--------|",
        *table_rows,
        "",
        "## Warnings",
        "\n".join(warnings) if warnings else "None",
        "",
        "## Errors",
        "\n".join(errors) if errors else "None",
        "",
        "## Next Actions",
        "Inspect database and verify UI renders warehouse items with unit prices correctly." if not errors else "Review error traceback in state.json and retry failed step."
    ]

    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"[REPORT] Execution report updated at {REPORT_FILE}")

def run_step(step, force=False):
    sid = step["id"]
    script_path = os.path.join(PIPELINE_DIR, step["script"])
    cmd = [sys.executable, script_path] + step["args"](step, PROJECT_ROOT)
    if force:
        cmd.append("--force")

    start_time = time.time()
    started_iso = datetime.now(timezone.utc).isoformat()
    print(f"\n========================================================")
    print(f"[*] RUNNING STEP: {sid}")
    print(f"[*] Command: {' '.join(cmd)}")
    print(f"========================================================")

    res = subprocess.run(cmd, cwd=PROJECT_ROOT)
    elapsed = time.time() - start_time
    finished_iso = datetime.now(timezone.utc).isoformat()

    if res.returncode == 0:
        print(f"[+] STEP {sid} COMPLETED SUCCESFULLY in {elapsed:.2f}s")
        return {
            "step_name": sid,
            "status": "SUCCESS",
            "started_at": started_iso,
            "finished_at": finished_iso,
            "duration_seconds": round(elapsed, 2),
            "output_path": step["output"],
            "attempt": 1,
            "error": None
        }, elapsed
    else:
        print(f"[-] STEP {sid} FAILED with return code {res.returncode}")
        return {
            "step_name": sid,
            "status": "FAILED",
            "started_at": started_iso,
            "finished_at": finished_iso,
            "duration_seconds": round(elapsed, 2),
            "output_path": step["output"],
            "attempt": 1,
            "error": {
                "type": "SubprocessError",
                "message": f"Script returned non-zero exit code {res.returncode}",
                "traceback": None
            }
        }, elapsed

def parse_args():
    parser = argparse.ArgumentParser(description="Master Warehouse Products Pipeline Orchestrator")
    parser.add_argument("--reset", "--clean", action="store_true", help="Wipe all artifacts and restart")
    parser.add_argument("--force", action="store_true", help="Force overwrite step outputs")
    parser.add_argument("--step", type=str, help="Run single isolated step")
    parser.add_argument("--from-step", type=str, help="Invalidate from step onward")
    parser.add_argument("--dry-run", action="store_true", help="Print plan and checkpoints without running")
    return parser.parse_args()

def main():
    args = parse_args()
    state = load_state()

    # Capability (a): Full Reset
    if args.reset:
        print(f"[!] Performing full reset of workspace: {WORKSPACE_DIR}")
        if os.path.exists(WORKSPACE_DIR):
            for item in os.listdir(WORKSPACE_DIR):
                item_path = os.path.join(WORKSPACE_DIR, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"[WARN] Failed to delete {item_path}: {e}")
        state = {}
        save_state(state)
        print("[+] Full reset complete.")
        if not args.force and not args.step and not args.from_step:
            return 0

    # Capability (b): Invalidate from step
    if args.from_step:
        step_ids = [s["id"] for s in STEPS]
        if args.from_step not in step_ids:
            print(f"[ERROR] Step {args.from_step} not recognized. Available: {step_ids}")
            return 1
        idx = step_ids.index(args.from_step)
        for s in STEPS[idx:]:
            sid = s["id"]
            if sid in state:
                del state[sid]
            if os.path.exists(s["output"]):
                try:
                    os.remove(s["output"])
                except Exception:
                    pass
        save_state(state)
        print(f"[+] Invalidated checkpoints from {args.from_step} onward.")

    # Capability (d): Dry-run
    if args.dry_run:
        print("\n=== DRY RUN / PLAN ===")
        for s in STEPS:
            sid = s["id"]
            info = state.get(sid, {})
            status = info.get("status", "NOT_RUN")
            exists = os.path.exists(s["output"])
            print(f"Step: {sid:35} | Status: {status:10} | Output Exists: {exists}")
        print("======================\n")
        return 0

    # Capability (c): Isolated Node Execution
    if args.step:
        target_step = next((s for s in STEPS if s["id"] == args.step), None)
        if not target_step:
            print(f"[ERROR] Step {args.step} not found.")
            return 1
        res_info, dur = run_step(target_step, force=args.force)
        state[args.step] = res_info
        save_state(state)
        generate_report(state, f"Single step {args.step}: {res_info['status']}", {args.step: dur})
        return 0 if res_info["status"] == "SUCCESS" else 1

    # Normal Sequential Graph Execution
    durations = {}
    for step in STEPS:
        sid = step["id"]
        info = state.get(sid, {})
        out_exists = os.path.exists(step["output"])

        # Smart Skip
        if info.get("status") == "SUCCESS" and out_exists and not args.force:
            print(f"[SKIP] Step {sid} already completed with SUCCESS checkpoint. Output exists.")
            continue

        res_info, dur = run_step(step, force=args.force)
        state[sid] = res_info
        durations[sid] = dur
        save_state(state)

        if res_info["status"] != "SUCCESS":
            generate_report(state, f"Pipeline halted at step {sid}", durations)
            return 1

    generate_report(state, "All steps in warehouse pipeline succeeded.", durations)
    return 0

if __name__ == '__main__':
    sys.exit(main())
