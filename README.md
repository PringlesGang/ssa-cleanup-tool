# ssa-cleanup-tool
A tool for cleaning up SubStationAlpha subtitle files for cleaner distribution, version control and build strategies.

This tool allows you to clean up a batch of SSA files at once, in various ways:
- keeping lines matching a whitelist and discarding lines matching a blacklist;
- replacing entire sections with predefined text.

Built for Python 3.11.9.

### Motivation
This tool could be useful for better management of SSA projects.
Only a single SSA file could be maintained, which could be parsed down to a _signs/songs_ file using filters, as well as automatically removing compiled effects for cleaner version control.
All comments could also be removed to de-bloat the final release.

### Experiencing issues?
Is the documentation unclear, or have you run into a bug? Feel free to open an issue, or come into contact. I'm happy to help!

Pull requests for bug fixes (or even new features!) are also always welcome! :)

# Contents
- [Main program](#main-program)
- [RegEx parser](#regex-parser)
    - [Syntax](#syntax)
    - [Behaviour](#behaviour)
    - [Exceptions](#exceptions)
- [Section replacer](#section-replacer)
    - [Syntax](#syntax-1)
    - [Behaviour](#behaviour-1)
    - [Exceptions](#exceptions-1)

# Main program
The program consists of multiple subprograms:
- **RegEx parser**: A parser that keeps or discards lines based on RegEx black- and whitelists.
- **Section replacer**: Replaces entire SSA sections with predefined custom text, or removes sections outright.

A comprehensive list of all available tools can be found with the `ssa-cleanup-tool.py -h` command.

# RegEx parser
This tool allows you to provide black- and whitelists of RegEx expressions, and have lines in the parsed SSA file either kept or discarded based on whether they match those expressions or not.

## Syntax
```
ssa-cleanup-tool.py parse-regex [-h] [-d] [-n] files [files ...] [-b BLACKLISTS [BLACKLISTS ...]] [-w WHITELISTS [WHITELISTS ...]] [-o OUTPUT [OUTPUT ...]]
```

### `files [files ...]` (list of paths)
A list paths to SSA files (or paths to directories; see [`-d`](#d---directory)) serving as the input that will be processed by the tool.

> [!IMPORTANT]
> Each file is expected to be in UTF-8.

### `[-h]`, `[--help]`
Print help documentation for the RegEx parser.

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

> [!IMPORTANT]
> Each file is expected to be in UTF-8.

### `[-w WHITELISTS [WHITELISTS ...]]`, `[--whitelist WHITELISTS [WHITELISTS ...]]` (list of paths)
This argument allows you to provide a list of paths to whitelist files. These files contain rules against which each line in the input will be tested. If none of these tests pass (i.e. no rule in the whitelists matches with the line), this line will not appear in the result.

> [!IMPORTANT]
> Each file is expected to be in UTF-8.

### `[-o OUTPUT [OUTPUT ...]]`, `[--output OUTPUT [OUTPUT ...]]` (list of paths)
Upon using this tag, a list **of equal length to the amount of input [`files`](#files-files--list-of-paths) provided must follow**, listing the output paths per input file, in order.

If not used, the parsed files will be saved in the `./output/` folder next to the main script under the same names as the input files.

> [!WARNING]
> This argument reacts unpredictably with the [`-d`](#d---directory) argument.

> [!IMPORTANT]
> If the amount of output paths passed is not exactly equal to the amount of [`files`](#files-files--list-of-paths) passed, the program will terminate with an error.


## Behaviour
Each filterlist (whitelist or blacklist) will be treated as a plaintext UTF-8, newline-separated list of RegEx rules.

- If there is no part of the line that matches with any of the rules in a whitelist, it is not written to the output.
- If there is a part that of the line that matches even one of the rules in the blacklist, it is not written to the output.
- If a line has a part that matches with a rule in the whitelist (or the whitelist is empty), and no part matches against any of the rules the blacklist, it is written to the output.

> [!NOTE]
> As this program checks against individual lines, and as each filter file is newline-separated, it is impossible to implement newlines in your RegEx rules.

## Exceptions
### InvalidOutputCountException
Raised if the amount of output paths does not match the amount of input files.

### NotAFileException
A filepath provided in the input files, whitelist or blacklists arguments does not lead to a file.

### NotADirectoryException
A filepath provided in the input files (in case of `-d`) or output paths argument does not lead to a directory.

# Section replacer
This tool allows you to replace entire sections of SSA files with pre-written custom ones.

Simply write an SSA file as you would normally, and all provided sections—denoted by a label in \[square brackets\]—in the input files will be replaced by what's below that label in the template files.

A section can also be removed outright, but entering `~[Section label]` in the template.

## Syntax
```
ssa-cleanup-tool.py replace-sections [-h] [-d] [-n] files [files ...] [-t TEMPLATES [TEMPLATES ...]] [-o OUTPUT [OUTPUT ...]]
```

### `files [files ...]` (list of paths)
A list paths to SSA files (or paths to directories; see [`-d`](#d---directory)) serving as the input that will be processed by the tool.

> [!IMPORTANT]
> Each file is expected to be in UTF-8.

### `[-h]`, `[--help]`
Print help documentation for the section replacer.

### `[-d]`, `[--directory]`
Adding this tag treats the provided [`files`](#files-files--list-of-paths) as directories. The program will search through these directories (non-recursively), and gather all files within to be used as input.

> [!NOTE]
> It is impossible to mix files and directories.

### `[-n]`, `[--no-delete]`
Adding this tag will make sure every file in the output folder will not be deleted, with exception to those files that will be overwritten by newly cleaned files with the same name.

> [!NOTE]
> No directories within the `./output/` directory (or anything within those directories) will be deleted, regardless of this tag.

### `[-t TEMPLATES [TEMPLATES ...]]`, `[--templates TEMPLATES [TEMPLATES ...]]` (list of paths)
This argument allows you to provide a list of paths to template files. These files contain the sections that need to be replaced, and what they need to be replaced with (or if they need to be removed outright).

> [!IMPORTANT]
> Each file is expected to be in UTF-8-BOM.

### `[-o OUTPUT [OUTPUT ...]]`, `[--output OUTPUT [OUTPUT ...]]` (list of paths)
Upon using this tag, a list **of equal length to the amount of input [`files`](#files-files--list-of-paths) provided must follow**, listing the output paths per input file, in order.

If not used, the parsed files will be saved in the `./output/` folder next to the main script under the same names as the input files.

> [!WARNING]
> This argument reacts unpredictably with the [`-d`](#d---directory) argument.

> [!IMPORTANT]
> If the amount of output paths passed is not exactly equal to the amount of [`files`](#files-files--list-of-paths) passed, the program will terminate with an error.

## Behaviour
Each template file will be treated as a plaintext UTF-8-BOM file, structured in the same way as a regular SSA file.

Each section, starting with a line consisting of a label between [square brackets] and nothing else, will define what the same section in the source files will be replaced with.

A section can be told te be removed outright by placing a '`~`' before the square-bracketed label. All text underneath, until the next label definition, will be ignored.

Redefinitions of the same section result in undefined behaviour.

## Exceptions

### InvalidOutputCountException
Raised if the amount of output paths does not match the amount of input files.

### NotAFileException
A filepath provided in the input files or template files arguments does not lead to a file.

### NotADirectoryException
A filepath provided in the input files (in case of -d) or output paths argument does not lead to a directory.
