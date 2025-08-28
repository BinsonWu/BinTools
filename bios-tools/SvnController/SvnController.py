import os
import sys
import subprocess
import getpass
import shutil
import argparse
import platform

def find_svn_dirs(root_path):
    """Recursively locate directories with .svn subfolders starting from root_path."""
    svn_dirs = []
    for dirpath, dirnames, _ in os.walk(root_path):
        if ".svn" in dirnames:
            svn_dirs.append(dirpath)
    return svn_dirs

def update_current_branch_revision(svn_dirs, branches_dir, password):
    """Update the .revision file of the current branch with the latest SVN revision."""
    current_branch = get_current_branch(branches_dir)
    if not current_branch:
        print("No current branch set. Skipping revision update.")
        return
    
    branch_folder = os.path.join(branches_dir, current_branch)
    if not os.path.exists(branch_folder):
        print(f"Current branch folder '{branch_folder}' not found. Skipping revision update.")
        return
    
    revision_file = os.path.join(branch_folder, ".revision")
    new_revision = get_svn_revision(svn_dirs[0], password) if svn_dirs else "unknown"
    with open(revision_file, 'w') as f:
        f.write(new_revision)

def update_svn_to_revision(svn_dirs, revision, password_file):
    """Update all SVN repositories to a specified revision (or HEAD if None)."""
    if not svn_dirs:
        print("No SVN directories found. Aborting update.")
        sys.exit(1)

    password = get_or_save_password(password_file)

    if revision:
        for svn_dir in svn_dirs:
            cmd = ["svn", "update", "--password", password, svn_dir, "-r", revision]
            print(f"Updating '{svn_dir}' to revision {revision}")
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                error_output = e.stderr.lower()
                if any(err in error_output for err in ["authentication failed", "e170001", "e215004"]):
                    print(f"Warning: SVN authentication failed during update for {svn_dir}: {e.stderr.strip()}")
                    response = input("Would you like to update the SVN password? (y/n): ").strip().lower()
                    if response == 'y':
                        password = update_password(password_file)
                        # Retry the command with the new password
                        try:
                            subprocess.run(cmd, check=True, capture_output=True, text=True)
                        except subprocess.CalledProcessError as retry_e:
                            print(f"Error updating SVN directory {svn_dir} after password update: {retry_e.stderr.strip()}")
                            print("Falling back to HEAD for all directories")
                            try:
                                subprocess.run(["svn", "update", "--password", password], check=True, capture_output=True, text=True)
                            except subprocess.CalledProcessError as fallback_e:
                                print(f"Error during fallback to HEAD: {fallback_e.stderr.strip()}")
                                sys.exit(1)
                    else:
                        print("Operation aborted due to invalid password.")
                        sys.exit(1)
                else:
                    print(f"Error updating SVN directory {svn_dir}: {e.stderr.strip()}")
                    print("Falling back to HEAD for all directories")
                    try:
                        subprocess.run(["svn", "update", "--password", password], check=True, capture_output=True, text=True)
                    except subprocess.CalledProcessError as fallback_e:
                        print(f"Error during fallback to HEAD: {fallback_e.stderr.strip()}")
                        sys.exit(1)
    else:
        print("Updating all SVN directories to HEAD")
        cmd = ["svn", "update", "--password", password]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.lower()
            if any(err in error_output for err in ["authentication failed", "e170001", "e215004"]):
                print(f"Warning: SVN authentication failed during update: {e.stderr.strip()}")
                response = input("Would you like to update the SVN password? (y/n): ").strip().lower()
                if response == 'y':
                    password = update_password(password_file)
                    # Retry the command with the new password
                    try:
                        subprocess.run(cmd, check=True, capture_output=True, text=True)
                    except subprocess.CalledProcessError as retry_e:
                        print(f"Error updating SVN directories after password update: {retry_e.stderr.strip()}")
                        sys.exit(1)
                else:
                    print("Operation aborted due to invalid password.")
                    sys.exit(1)
            else:
                print(f"Error updating SVN directories: {e.stderr.strip()}")
                sys.exit(1)

def revert_svn_directories(svn_dirs):
    """Revert all local changes in the specified SVN repositories."""
    print(f"Reverting local changes in all SVN directories")
    for svn_dir in svn_dirs:
        try:
            subprocess.run(["svn", "revert", "-R", svn_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error reverting SVN directories: {e}")
            return

def get_svn_revision(svn_dir, password_file):
    """Retrieve the current SVN revision of a repository."""
    password = get_or_save_password(password_file)
    
    if not test_svn_password(svn_dir, password):
        print("Warning: SVN authentication failed. The stored password may be incorrect.")
        response = input("Would you like to update the SVN password? (y/n): ").strip().lower()
        if response == 'y':
            password = update_password(password_file)
        else:
            print("Operation aborted due to invalid password.")
            sys.exit(1)

    cmd = ["svn", "info", "--show-item", "revision", "--password", password]
    try:
        result = subprocess.run(cmd, cwd=svn_dir, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.lower()
        if any(err in error_output for err in ["authentication failed", "e170001", "e215004"]):
            print(f"Warning: SVN authentication failed during revision check: {e.stderr.strip()}")
            response = input("Would you like to update the SVN password? (y/n): ").strip().lower()
            if response == 'y':
                password = update_password(password_file)
                # Retry the command with the new password
                try:
                    result = subprocess.run(cmd, cwd=svn_dir, check=True, capture_output=True, text=True)
                    return result.stdout.strip()
                except subprocess.CalledProcessError as retry_e:
                    print(f"Error getting revision for {svn_dir} after password update: {retry_e.stderr.strip()}")
                    sys.exit(1)
            else:
                print("Operation aborted due to invalid password.")
                sys.exit(1)
        else:
            print(f"Error getting revision for {svn_dir}: {e.stderr.strip()}")
            return "unknown"

def diff_svn_directories(svn_dirs, revision, password, output_dir=None):
    """Generate diff patch files for each SVN working copy against a revision (or HEAD if None)."""
    patch_files = []
    for svn_dir in svn_dirs:
        cmd = ["svn", "diff", "--password", password]
        if revision:
            print(f"Generating diff for {svn_dir} against revision {revision}")
            cmd.extend(["-r", revision])
        else:
            print(f"Generating diff for {svn_dir} against HEAD")
        
        try:
            result = subprocess.run(cmd, cwd=svn_dir, check=True, capture_output=True, text=True)
            if result.stdout:
                if output_dir:
                    safe_dir_name = svn_dir.replace(os.sep, '_').replace(':', '_')
                    patch_filename = os.path.join(output_dir, f"patch_{safe_dir_name}.patch")
                    os.makedirs(os.path.dirname(patch_filename), exist_ok=True)
                    with open(patch_filename, 'w') as f:
                        f.write(result.stdout)
                    print(f"Diff saved to {patch_filename}")
                    patch_files.append(patch_filename)
                else:
                    print(result.stdout)
            else:
                print(f"No changes found in {svn_dir}")
            if result.stderr:
                print(f"Warnings/Errors: {result.stderr}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error diffing {svn_dir}: {e}")
            return
    return patch_files

def apply_svn_patch(svn_dirs, patch_file_or_dir, password):
    """Apply a single patch file or all patches in a directory to matching SVN repositories."""
    if os.path.isdir(patch_file_or_dir):
        patch_files = [os.path.join(patch_file_or_dir, f) for f in os.listdir(patch_file_or_dir) if f.endswith('.patch')]
        if not patch_files:
            print(f"No patches found in {patch_file_or_dir}; no changes applied.")
            return
        for svn_dir in svn_dirs:
            safe_dir_name = svn_dir.replace(os.sep, '_').replace(':', '_')
            matching_patch = next((pf for pf in patch_files if f"patch_{safe_dir_name}.patch" in pf), None)
            if matching_patch and os.path.exists(matching_patch):
                print(f"Applying {matching_patch} to {svn_dir}")
                try:
                    subprocess.run(["svn", "patch", matching_patch, "--password", password], cwd=svn_dir, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error applying patch to {svn_dir}: {e}")
                    return
            else:
                print(f"No matching patch found for {svn_dir}")
    else:
        if not os.path.exists(patch_file_or_dir):
            print(f"Error: Patch file {patch_file_or_dir} does not exist.")
            sys.exit(1)
        print(f"Applying {patch_file_or_dir} to all SVN directories")
        try:
            subprocess.run(["svn", "patch", patch_file_or_dir, "--password", password] + svn_dirs, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error applying patch to SVN directories: {e}")
            return

def commit_svn_directories(svn_dirs, password):
    """Commit all changes in the specified SVN repositories, opening an editor for the message."""
    print(f"Committing changes in all SVN directories (editor will open for message)...")
    try:
        subprocess.run(["svn", "commit", "--password", password] + svn_dirs, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error committing SVN directories: {e}")
        return

def status_svn_directories(password):
    """Show status of all SVN repositories, default with -q to suppress unversioned files."""
    try:
        result = subprocess.run(["svn", "status", "-q", "--password", password], check=True, capture_output=True, text=True)
        print(result.stdout if result.stdout else "No changes found.")
        if result.stderr:
            print(f"Warnings/Errors: {result.stderr}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error checking status: {e}")
        return

def info_svn_directories(svn_dirs, password):
    """Show SVN info for all repositories."""
    print("Retrieving info for all SVN directories")
    try:
        result = subprocess.run(["svn", "info", "--password", password] + svn_dirs, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/Errors: {result.stderr}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving info: {e}")
        return

def log_svn_directories(args, svn_dirs, password):
    """Show SVN log for all repositories."""
    if len(args) < 1:
        print("Error: Log command requires a number.")
        print("Usage: python SvnController.py log <number>")
        sys.exit(1)
    print("Retrieving log for all SVN directories")
    try:
        if args[0].isdigit():
            for svn_dir in svn_dirs:
                print(svn_dir)
                result = subprocess.run(["svn", "log", "-l", str(int(args[0])), "--password", password], cwd=svn_dir, check=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"Warnings/Errors: {result.stderr}", file=sys.stderr)
                    sys.exit(1)
        else:
            print("Error: 'log' requires a number.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving log: {e}")
        return

def get_or_save_password(password_file):
    """Retrieve SVN password from a file or prompt user and save it securely."""
    is_windows = platform.system() == "Windows"

    # Check if the password file exists
    if os.path.exists(password_file):
        try:
            with open(password_file, 'r') as f:
                return f.read().strip()
        except PermissionError:
            print(f"Error: No read permission for {password_file}. "
                  f"Run {'as administrator' if is_windows else 'with sudo'} to fix.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading password file: {e}")
            sys.exit(1)

    # If file doesn't exist, prompt user for password
    return update_password(password_file)  # Use update_password to handle initial save

def test_svn_password(svn_dir, password):
    """Test if the provided SVN password is valid by running a simple SVN command."""
    cmd = ["svn", "update", "--password", password]
    try:
        result = subprocess.run(cmd, cwd=svn_dir, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.lower()
        # Check for authentication-related errors
        if any(err in error_output for err in ["authentication failed", "e170001", "e215004"]):
            print(f"SVN password test failed for {svn_dir}: {e.stderr.strip()}")
            return False
        else:
            print(f"Non-authentication error testing password for {svn_dir}: {e.stderr.strip()}")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error testing password for {svn_dir}: {e}")
        sys.exit(1)

def prepare_svn_operation(directory_path):
    """Validate directory path and locate SVN repositories."""
    directory_path = os.path.abspath(directory_path)
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        sys.exit(1)
    svn_directories = find_svn_dirs(directory_path)
    if not svn_directories:
        print("No SVN repositories found in the specified directory.")
        sys.exit(0)
    return svn_directories

def get_current_branch(branches_dir):
    """Read the current branch name from the .current_branch file."""
    current_branch_file = os.path.join(branches_dir, ".current_branch")
    if os.path.exists(current_branch_file):
        with open(current_branch_file, 'r') as f:
            return f.read().strip()
    return None

def set_current_branch(branches_dir, branch_name):
    """Record the current branch name in the .current_branch file."""
    current_branch_file = os.path.join(branches_dir, ".current_branch")
    os.makedirs(branches_dir, exist_ok=True)
    with open(current_branch_file, 'w') as f:
        f.write(branch_name)
    print(f"Current branch set to '{branch_name}'")

def branch_create(svn_dirs, branch_name, password, branches_dir):
    """Create a new branch by saving diffs and revision in a branch-specific folder."""
    branch_folder = os.path.join(branches_dir, branch_name)
    if os.path.exists(branch_folder):
        print(f"Error: Branch '{branch_name}' already exists.")
        sys.exit(1)

    os.makedirs(branch_folder, exist_ok=True)
    print(f"Created branch folder: {branch_folder}")

    set_current_branch(branches_dir, branch_name)

    revision = get_svn_revision(svn_dirs[0], password) if svn_dirs else "unknown"
    with open(os.path.join(branch_folder, ".revision"), 'w') as f:
        f.write(revision)
    print(f"Recorded revision {revision} for branch '{branch_name}'")

    patch_files = diff_svn_directories(svn_dirs, None, password, branch_folder)
    print(f"Branch '{branch_name}' created{' with patches' if patch_files else ' with no changes'} in {branch_folder}")

def branch_delete(branch_name, branches_dir):
    """Delete a branch by removing its folder, with safety checks."""
    branch_folder = os.path.join(branches_dir, branch_name)
    if not os.path.exists(branch_folder):
        print(f"Error: Branch '{branch_name}' does not exist.")
        sys.exit(1)
    if branch_name == "default":
        print("Error: Cannot delete the 'default' branch.")
        sys.exit(1)
    if branch_name == get_current_branch(branches_dir):
        print("Error: Cannot delete the current branch.")
        sys.exit(1)
    
    shutil.rmtree(branch_folder)
    print(f"Branch '{branch_name}' deleted.")

def branch_switch(svn_dirs, branch_name, password, branches_dir):
    """Switch to a branch by updating to its revision and applying patches."""
    branch_folder = os.path.join(branches_dir, branch_name)
    if not os.path.exists(branch_folder):
        print(f"Error: Branch '{branch_name}' does not exist.")
        sys.exit(1)

    # Update the current branch.
    current_branch = get_current_branch(branches_dir)
    current_branch_folder = os.path.join(branches_dir, current_branch)
    if current_branch and current_branch != branch_name:
        print(f"Updating current branch '{current_branch}' before switching...")

        if os.path.exists(current_branch_folder):
            shutil.rmtree(current_branch_folder)
        os.makedirs(current_branch_folder, exist_ok=True)

        update_current_branch_revision(svn_dirs, branches_dir, password)

        diff_svn_directories(svn_dirs, None, password, current_branch_folder)

    # Update to the target branch.
    current_revision_file = os.path.join(current_branch_folder, ".revision")
    current_revision = None
    if os.path.exists(current_revision_file):
        with open(current_revision_file, 'r') as f:
            current_revision = f.read().strip()
        print(f"Switching to branch '{current_branch_folder}' at revision {current_revision}...")
    else:
        print(f"No revision recorded for '{current_branch_folder}', using HEAD...")
    target_revision_file = os.path.join(branch_folder, ".revision")
    target_revision = None
    if os.path.exists(target_revision_file):
        with open(target_revision_file, 'r') as f:
            target_revision = f.read().strip()
        print(f"Switching to branch '{branch_name}' at revision {target_revision}...")
    else:
        print(f"No revision recorded for '{branch_name}', using HEAD...")

    revert_svn_directories(svn_dirs)
    if current_revision != target_revision:
        update_svn_to_revision(svn_dirs, target_revision, password)
    else:
        print(f"In the same code base, ignore the update to revision...")
    apply_svn_patch(svn_dirs, branch_folder, password)
    set_current_branch(branches_dir, branch_name)
    print(f"Switched to branch '{branch_name}'")

def branch_list(branches_dir):
    """List all branches with their revisions, marking the current branch."""
    if not os.path.exists(branches_dir):
        print("No branches exist.")
        return
    
    branches = [d for d in os.listdir(branches_dir) if os.path.isdir(os.path.join(branches_dir, d)) and not d.startswith('.')]
    current_branch = get_current_branch(branches_dir)
    if branches:
        print("Available branches:")
        for branch in branches:
            marker = " <-- (current)" if branch == current_branch else ""
            revision_file = os.path.join(branches_dir, branch, ".revision")
            revision = "unknown" if not os.path.exists(revision_file) else open(revision_file).read().strip()
            print(f"  - {branch} (revision: {revision}){marker}")
    else:
        print("No branches exist.")

def handle_branch_command(directory_path, args, svn_dirs, password):
    """Process branch subcommands (create, delete, switch, list)."""
    if len(args) < 1:
        print("Error: Branch command requires a subcommand.")
        print("Usage: python SvnController.py branch <subcommand> [<branch_name>]")
        print("Subcommands: create <branch_name>, delete <branch_name>, switch <branch_name>, list")
        sys.exit(1)

    branches_dir = os.path.join(directory_path, ".svn_branches")
    default_branch = "default"
    default_branch_folder = os.path.join(branches_dir, default_branch)

    branch_subcommand = args[0].lower()

    if not os.path.exists(default_branch_folder):
        print("Initializing 'default' branch and create 'systemp' branch for the current code ...")
        temp_branch = "systemp"
        branch_create(svn_dirs, temp_branch, password, branches_dir)
        branch_create(svn_dirs, default_branch, password, branches_dir)
        revert_svn_directories(svn_dirs)
        branch_switch(svn_dirs, temp_branch, password, branches_dir)
        print("Initializing 'default' branch and create 'systemp' branch done !!!\n")

    if branch_subcommand == "create":
        if len(args) != 2:
            print("Usage: python SvnController.py branch create <branch_name>")
            sys.exit(1)
        branch_create(svn_dirs, args[1], password, branches_dir)
        branch_switch(svn_dirs, args[1], password, branches_dir)
    
    elif branch_subcommand == "delete":
        if len(args) != 2:
            print("Usage: python SvnController.py branch delete <branch_name>")
            sys.exit(1)
        branch_delete(args[1], branches_dir)
    
    elif branch_subcommand == "switch":
        if len(args) != 2:
            print("Usage: python SvnController.py branch switch <branch_name>")
            sys.exit(1)
        branch_switch(svn_dirs, args[1], password, branches_dir)
    
    elif branch_subcommand == "list":
        if len(args) != 1:
            print("Usage: python SvnController.py branch list")
            sys.exit(1)
        update_current_branch_revision(svn_dirs, branches_dir, password)
        branch_list(branches_dir)
    
    else:
        print("Error: Unknown subcommand. Use: create, delete, switch, list")
        sys.exit(1)

def update_password(password_file):
    """Prompt user for a new SVN password and update it securely in the password file."""
    is_windows = platform.system() == "Windows"

    # Prompt user for new password
    new_password = getpass.getpass("Enter new SVN password (will overwrite existing password): ")

    try:
        if is_windows:
            # Windows: Write the file directly and set permissions with icacls
            with open(password_file, 'w') as f:
                f.write(new_password)
            
            # Set file permissions (restrict to current user)
            subprocess.run(
                ['icacls', password_file, '/inheritance:r'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            subprocess.run(
                ['icacls', password_file, '/grant:r', f'{os.getlogin()}:F'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            # Unix-like: Use sudo and tee to write, then set permissions
            subprocess.run(
                f"echo '{new_password}' | sudo tee {password_file}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            subprocess.run(['sudo', 'chmod', '777', password_file], check=True)  # Restrict to owner only
            subprocess.run(['sudo', 'chown', os.getlogin(), password_file], check=True)  # Set owner to current user
            subprocess.run(['sudo', 'chgrp', os.getlogin(), password_file], check=True)  # Set group to current user

        print(f"SVN password updated successfully in {password_file}")
        return new_password
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to {'set permissions on' if is_windows else 'save password to'} "
              f"{password_file}: {e}")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Insufficient permissions to write to {password_file}. "
              f"Run {'as administrator' if is_windows else 'with sudo'}.")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating password: {e}")
        sys.exit(1)

def get_usage_message():
    """Return the usage message for the SVN Utility Script."""
    return """
SVN Utility Script
==================
A command-line tool to manage Subversion (SVN) repositories and custom branching workflows in the current or specified directory.

Usage:
  python SvnController.py <command> [<arguments>]
  If using the packaged tool:
    - On Linux: Replace `python SvnController.py` with `SvnController`.
    - On Windows: Replace `python SvnController.py` with `SvnController.exe`.

Commands (aliases in parentheses):
  update (up) [<revision>]
    Updates all SVN repositories to a specified revision. If no revision is provided, defaults to the latest (HEAD).
    Example: `python SvnController.py update 1234` or `python SvnController.py up 1234`

  revert (rv)
    Reverts all local changes in the SVN repositories within the current directory, restoring them to the last committed state.
    Example: `python SvnController.py revert` or `python SvnController.py rv`

  diff (df) [r <revision>] [o <output_dir>]
    Generates diff patch files for each SVN working copy against a specified revision (or HEAD if omitted).
    Options:
      - r <revision>: Specify the revision to compare against (e.g., 1234).
      - o <output_dir>: Save patches to the specified directory; otherwise, diffs are printed to the console.
    Example: `python SvnController.py diff r 1234 o ./patches` or `python SvnController.py df r 1234 o ./patches`

  apply (ap) <patch_file_or_dir>
    Applies a single patch file or all patch files in a directory to the matching SVN repositories.
    - If a file is provided, it applies to all repositories.
    - If a directory is provided, it applies patches matching each repository's name.
    Example: `python SvnController.py apply patch_file.patch` or `python SvnController.py ap patch_file.patch`

  commit (ci)
    Commits all changes in the SVN repositories, opening a text editor (e.g., Vim) for the commit message.
    Example: `python SvnController.py commit` or `python SvnController.py ci`

  status (st)
    Displays the status of all SVN repositories in the current directory, using quiet mode (-q) to suppress unversioned files.
    Example: `python SvnController.py status` or `python SvnController.py st`

  info (inf)
    Retrieves and displays detailed SVN information for all repositories in the current directory.
    Example: `python SvnController.py info` or `python SvnController.py inf`

  log (lg)
    Retrieves and displays detailed SVN log information for all repositories in the current directory.
    Example: `python SvnController.py log` or `python SvnController.py lg`

  branch (br) <subcommand> [<branch_name>]
    Manages custom branches stored locally in `.svn_branches/`:
      - create <branch_name>: Creates a new branch, capturing the current state with diffs and revision.
        Example: `python SvnController.py branch create mybranch` or `python SvnController.py br create mybranch`
      - delete <branch_name>: Deletes an existing branch (cannot delete 'default' or the current branch).
        Example: `python SvnController.py branch delete mybranch` or `python SvnController.py br delete mybranch`
      - switch <branch_name>: Switches to a branch by reverting changes, updating to its revision, and applying patches.
        Example: `python SvnController.py branch switch mybranch` or `python SvnController.py br switch mybranch`
      - list: Lists all branches with their revisions, marking the current branch.
        Example: `python SvnController.py branch list` or `python SvnController.py br list`

  update-password (up-pw)
    Updates the stored SVN password by prompting the user for a new password and saving it securely.
    Example: `python SvnController.py update-password` or `python SvnController.py up-pw`
"""

if __name__ == "__main__":
    # Define command aliases
    command_aliases = {
        'up': 'update',
        'rv': 'revert',
        'df': 'diff',
        'ap': 'apply',
        'ci': 'commit',
        'st': 'status',
        'inf': 'info',
        'lg': 'log',
        'br': 'branch',
        'up-pw': 'update-password'
    }

    # Define valid full commands for the ArgumentParser choices
    valid_commands = [
        "update", "revert", "diff", "apply", "commit", "status", "info", "log", "branch", "update-password"
    ]

    # Initialize ArgumentParser with the usage message from the function
    parser = argparse.ArgumentParser(
        description=get_usage_message(),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command", help="Command to execute (full command or alias)")
    parser.add_argument("command_args", nargs="*", help="Arguments for the specified command")

    args = parser.parse_args()

    # Map the provided command to its full command if it's an alias
    input_command = args.command.lower()
    resolved_command = command_aliases.get(input_command, input_command)

    # Validate the resolved command
    if resolved_command not in valid_commands:
        print(f"Error: Unknown command or alias '{args.command}'. Use one of: {', '.join(valid_commands)} "
              f"or aliases: {', '.join(command_aliases.keys())}")
        sys.exit(1)

    # Define the password file location based on OS
    if platform.system() == "Windows":
        password_file = r"C:\svn_config\svn_password"
        os.makedirs(os.path.dirname(password_file), exist_ok=True)
    else:
        password_file = "/etc/svn_password"

    # Handle the commands using the resolved command
    if resolved_command == "update-password":
        if args.command_args:
            print("Error: 'update-password' does not accept additional arguments.")
            sys.exit(1)
        update_password(password_file)

    else:
        # Set the working directory to the current directory
        directory_path = os.getcwd()

        # Locate SVN repositories in the working directory
        svn_directories = prepare_svn_operation(directory_path)

        # Handle commands requiring SVN operations
        if resolved_command == "update":
            revision = args.command_args[0] if args.command_args else None
            update_svn_to_revision(svn_directories, revision, password_file)
            branches_dir = os.path.join(directory_path, ".svn_branches")
            update_current_branch_revision(svn_directories, branches_dir, password_file)

        elif resolved_command == "revert":
            revert_svn_directories(svn_directories)

        elif resolved_command == "diff":
            revision = None
            output_dir = None
            i = 0
            while i < len(args.command_args):
                if args.command_args[i] == "r":
                    if i + 1 < len(args.command_args):
                        revision = args.command_args[i + 1]
                        i += 2
                    else:
                        print("Error: 'r' requires a revision number.")
                        sys.exit(1)
                elif args.command_args[i] == "o":
                    if i + 1 < len(args.command_args):
                        output_dir = args.command_args[i + 1]
                        i += 2
                    else:
                        print("Error: 'o' requires an output directory.")
                        sys.exit(1)
                else:
                    i += 1
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            diff_svn_directories(svn_directories, revision, password_file, output_dir)

        elif resolved_command == "apply":
            if not args.command_args:
                print("Error: 'apply' requires a patch file or directory.")
                sys.exit(1)
            apply_svn_patch(svn_directories, args.command_args[0], password_file)

        elif resolved_command == "commit":
            commit_svn_directories(svn_directories, password_file)

        elif resolved_command == "status":
            status_svn_directories(password_file)

        elif resolved_command == "info":
            info_svn_directories(svn_directories, password_file)

        elif resolved_command == "log":
            log_svn_directories(args.command_args, svn_directories, password_file)

        elif resolved_command == "branch":
            handle_branch_command(directory_path, args.command_args, svn_directories, password_file)