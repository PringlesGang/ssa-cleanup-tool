# ssa-cleanup-tool
A tool for cleaning up SubStationAlpha subtitle files for cleaner distribution, version control and build strategies.

This tool allows you to clean up a batch of SSA files at once, keeping lines matching a whitelist and discarding lines matching a blacklist.

### Motivation
This tool could be useful for better management of SSA projects.
Only a single SSA file could be maintained, which could be parsed down to a _signs/songs_ file using filters, as well as automatically removing compiled effects for cleaner version control.
All comments could also be removed to de-bloat the final release.

### Experiencing issues?
Is the documentation unclear, or have you run into a bug? Feel free to open an issue, or come into contact. I'm happy to help!

Pull requests for bug fixes (or even new features!) are also always welcome! :)

# Contents
- [How to use](#how-to-use)
    - [Arguments](#arguments)
- [Behaviour](#behaviour)
    - [Main program](#main-program)
    - [Whitelist/blacklist parsing](#whitelistblacklist-parsing)
    - [Exceptions](#exceptions)

# How to use
To process a number of SSA files, simply run the script `ssa-cleanup-tool.py` with command-line arguments to suit your needs:
```
ssa-cleanup-tool.py files [files ...] [-d] [-n] [-b BLACKLISTS [BLACKLISTS ...]] [-w WHITELISTS [WHITELISTS ...]] [-o OUTPUTNAMES [OUTPUTNAMES ...]]
```

Alternatively it can be imported as a module, after which the following function can be accessed:
```py
def ssaCleanup(
    files: List[str],
    blacklists: Set[str] = set(),
    whitelists: Set[str] = set(),
    outputNames: List[str] = [],
    directory: bool = False,
    delete: bool = False,
) -> None:
```

## Arguments

### `files [files ...]` (list of paths)
A list paths to SSA files (or paths to directories; see [`-d`](#d---directory)) serving as the input that will be processed by the tool.

### `[-d]`, `[--directory]`
Adding this tag treats the provided [`files`](#files-files--list-of-paths) as directories. The program will search through these directories (non-recursively), and gather all files within to be used as input.

> [!NOTE]
> It is impossible to mix files and directories.

### `[-n]`, `[--no-delete]`
Adding this tag will make sure every file in the output folder will not be deleted, with exception to those files that will be overwritten by newly cleaned files with the same name.

> [!NOTE]
> No directories within the `./output/` directory (or anything within those directories) will be deleted, regardless of this tag.

### `[-b BLACKLISTS [BLACKLISTS ...]]`, `[--blacklist BLACKLISTS [BLACKLISTS ...]]` (list of paths)
This argument allows you to provide a list of paths to blacklist files. These files contain rules against which each line in the input will be tested. If even one of these tests passes (i.e. it matches what is stated within the blacklist), this line will not appear in the result.

### `[-w WHITELISTS [WHITELISTS ...]]`, `[--whitelist WHITELISTS [WHITELISTS ...]]` (list of paths)
This argument allows you to provide a list of paths to whitelist files. These files contain rules against which each line in the input will be tested. If none of these tests pass (i.e. no rule in the whitelists matches with the line), this line will not appear in the result.

### `[-o OUTPUTNAMES [OUTPUTNAMES ...]]`, `[--output OUTPUTNAMES [OUTPUTNAMES ...]]` (list of strings)
Upon using this tag, a list **of equal length to the amount of input [`files`](#files-files--list-of-paths) provided must follow**, listing the output names per input file, in order. These files will be placed under the provided name in the outputs folder.

> [!WARNING]
> This argument reacts unpredictably with the [`-d`](#d---directory) argument.

> [!IMPORTANT]
> If the amount of output names passed is not exactly equal to the amount of [`files`](#files-files--list-of-paths) passed, the program will terminate with an error.

# Behaviour
## Main program
This program will first clear out all files the `./output/` directory (creating it if it doesn't exist, and not clearing it in case of `-n`).
It will then take all files specified black- and whitelists in the `-b` and `-w`, and parse every rule mentioned within.
Next, it will take all files mentioned in the `files` section (taking all files in those _directories_ instead, in case of `-d`), and match them with their respective output name as given in `-o`, defaulting to their original names if this argument is not provided.

For each of these pairs, a file with the corresponding output name is created in the `./output/` directory (or overwritten if a file under the same name is already there), and the input will be read line-by-line. Each line will be tested; being written into the output file if and only if
- the line matches **at least one rule** in any of the whitelists (or if there are no whitelist rules given), and
- the line matches **not a single rule** specified in any of the blacklists.

## Whitelist/blacklist parsing
Each filterlist (whitelist or blacklist) will be treated as a plaintext, newline-separated list of RegEx rules.

- If there is no part of the line that matches with any of the rules in a whitelist, it is not written to the output.
- If there is a part that of the line that matches even one of the rules in the blacklist, it is not written to the output.
- If a line has a part that matches with a rule in the whitelist (or the whitelist is empty), and no part matches against any of the rules the blacklist, it is written to the output.

> [!NOTE]
> As this program checks against individual lines, and as each filter file is newline-separated, it is impossible to implement newlines in your RegEx rules.

## Exceptions
### InvalidOutputNamesCountException
Raised if the amount of output names does not match the amount of input files.

### NotAFileException
A filepath provided in the input files, whitelist or blacklists arguments does not lead to a file.

### NotADirectoryException
A filepath provided in the input files argument does not lead to a directory, and the `-d` flag is set.
