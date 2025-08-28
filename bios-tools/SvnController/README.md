# Usage
python SvnController.py <command> [<arguments>]
If using the packaged tool:
  - On Linux: Replace `python SvnController.py` with `SvnController`.
  - On Windows: Replace `python SvnController.py` with `SvnController.exe`.

# Commands
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

# Prepare
## Python
### WSL Ubuntu-20.04
#### 3.8
sudo apt update
sudo apt install python3

#### 3.10
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 -y
sudo apt install libpython3.10-dev -y

### Windows
Please refer to "https://www.python.org/".

# Build
## Linux
cd SvnController
bash BuildTool.sh

## Windows
cd SvnController
BuildTool.bat
