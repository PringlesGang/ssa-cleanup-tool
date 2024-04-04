import argparse
import os
import sys
import re

from typing import Any, Iterable, List, Set, Pattern, NamedTuple
from pathlib import Path


outputDir = Path("./output")


class IOPair(NamedTuple):
    input: Path
    output: Path


def flattenOnce(iterable: Iterable[Iterable[Any]]) -> Iterable[Any]:
    """Flatten one level of a multi-level Iterable."""
    return [item for item in [deepIterable for deepIterable in iterable]]


def getFilesInDirectories(directories: List[Path]) -> List[Path]:
    """Get all files within the provided directories.
    Not recursive!
    """
    files: List[Path] = []
    
    for directory in directories:
        files += [file for file in directory.iterdir() if file.is_file()]
        
    return files


def parseArguments() -> argparse.Namespace:
    """Parse the command-line arguments passed into the program."""
    parser = argparse.ArgumentParser(description="Clean up SubStationAlpha files.")

    parser.add_argument("files", type=str, nargs='+',
                        help="Filepaths to the ssa files, or directories containing them.")
    parser.add_argument("-d", "--directory", dest="directory", action="store_true",
                        help="Treat the provided input files as directories containing the input files.")
    parser.add_argument("-n", "--no-delete", dest="delete", action="store_false",
                        help="Don't clear out the output directory.")
    parser.add_argument("-b", "--blacklist", dest="blacklists", type=str, nargs='+', default=[],
                        help="Filepaths to newline-separated blacklist files.")
    parser.add_argument("-w", "--whitelist", dest="whitelists", type=str, nargs='+', default=[],
                        help="Filepaths to newline-separated whitelist files.")
    parser.add_argument("-o", "--output", dest="outputNames", type=str, nargs='+', default=[],
                        help="Output names for each given input, in order.")

    return parser.parse_args()


def checkArguments(
    files: List[str],
    blacklists: Set[str],
    whitelists: Set[str],
    outputNames: List[str],
    directory: bool,
    delete: bool,
) -> None:
    """Check all arguments for validity."""
    # Check if there is a bijection between the input files and output names
    if outputNames and len(outputNames) != len(files):
        print("The amount of output names does not match the amount of input files.")
        exit(1)


def getInputPaths(
    files: List[str],
    blacklists: Set[str],
    whitelists: Set[str],
    directory: bool,
) -> List[Path]:
    """Convert the input files list into a list of Paths, and coalless the directories if necessary."""
    # Check if all files exist
    inputPaths = list(map(Path, files))
    allFiles = map(Path, set(inputPaths).union(blacklists).union(whitelists))
    if directory:
        nonexistentDirectory = next((directory for directory in inputPaths if not directory.is_dir()), None)
        if nonexistentDirectory is not None:
            print(f"{nonexistentDirectory} is not a directory.", file=sys.stderr)
            exit(1)
        inputPaths = getFilesInDirectories(inputPaths)
    else:
        nonexistentFile = next((file for file in allFiles if not file.is_file()), None)
        if nonexistentFile is not None:
            print(f"{nonexistentFile} is not a file.", file=sys.stderr)
            exit(1)
    
    return inputPaths


def getIOPairs(
    files: List[str],
    blacklists: Set[str],
    whitelists: Set[str],
    outputNames: List[str],
    directory: bool,
) -> Set[IOPair]:
    """Pair up the input paths with the corresponding output paths."""
    inputPaths = getInputPaths(
        files,
        blacklists,
        whitelists,
        directory
    )
    
    return set(
        map( # Map to IOPair
            lambda pair: IOPair(pair[0], pair[1]),
            zip( # Pair up input files and output files
                inputPaths,
                map( # Get output path
                    lambda name: outputDir.joinpath(name),
                    # Use output names if provided; otherwise use input names
                    outputNames if outputNames else list(map(lambda file: Path(file).name, inputPaths)))
                )
            )
        )


def acceptedByWhitelist(line: str, whitelist: Set[Pattern[str]]) -> bool:
    """Check whether the provided line adheres to the whitelist."""
    return whitelist == set() or next((line for rule in whitelist if rule.match(line)), None) is not None


def acceptedByBlacklist(line: str, blacklist: Set[Pattern[str]]) -> bool:
    """Check whether the provided line adheres to the blacklist."""
    return next((line for rule in blacklist if rule.match(line)), None) is None


def processFilterList(filterPathSet: Set[str]) -> Set[Pattern[str]]:
    """Convert a list of filter files into a list of RegEx Pattern objects."""
    filterFileSet = map(Path, filterPathSet)
    
    filterSet: Set[Pattern[str]] = set()
    for filterFile in filterFileSet:
        with open(filterFile, 'r') as fileStream:
            for line in fileStream:
                try:
                    filter = re.compile(line.removesuffix('\n'))
                except re.error:
                    print(f"{line} in {filterFile} is not a valid regular expression; ignoring.", file=sys.stderr)
                else:
                    filterSet.add(filter)

    return filterSet


def processFile(
    ssaFile: IOPair,
    whitelist: Set[Pattern[str]],
    blacklist: Set[Pattern[str]],
) -> None:
    """Clean up a single ssa file."""
    if ssaFile.output.exists():
        os.remove(ssaFile.output)
    
    with open(ssaFile.input, 'r') as inputStream:
        with open(ssaFile.output, 'x') as outputStream:
            for line in filter(
                lambda line: acceptedByWhitelist(line, whitelist) and acceptedByBlacklist(line, blacklist),
                inputStream
            ):
                outputStream.write(line)


def ssaCleanup(
    files: List[str],
    blacklists: Set[str] = set(),
    whitelists: Set[str] = set(),
    outputNames: List[str] = [],
    directory: bool = False,
    delete: bool = False,
) -> None:
    """Clean up SubStationAlpha files by means of black- and whitelists.

    Args:
        files (List[str]): Filepaths to the ssa files, or directories containing them.
        blacklist (List[str], optional): Filepaths to newline-separated blacklist files. Defaults to set().
        whitelist (List[str], optional): Filepaths to newline-separated whitelist files. Defaults to set().
        outputNames (List[str], optional): Output names for each given input, in order. Defaults to [].
        directory (bool, optional): Set to True if the `files` argument consists of directories. Defaults to False.
        delete (bool, optional): Set to True if you want the program to clear the output directory first. Defaults to False.
    """
    checkArguments(
        files,
        blacklists,
        whitelists,
        outputNames,
        directory,
        delete
    )
    
    IOPairs = getIOPairs(
        files,
        blacklists,
        whitelists,
        outputNames,
        directory
    )
    whitelist = processFilterList(whitelists)
    blacklist = processFilterList(blacklists)
    
    # Create the output directory
    if not outputDir.is_dir():
        outputDir.mkdir()
    
    if delete:
        for file in [file for file in outputDir.iterdir() if file.is_file()]:
            os.remove(file)
    
    for ssaFile in IOPairs:
        processFile(ssaFile, whitelist, blacklist)


if __name__ == "__main__":
    args = parseArguments()
    ssaCleanup(
        args.files,
        args.blacklists,
        args.whitelists,
        args.outputNames,
        args.directory,
        args.delete,
    )
