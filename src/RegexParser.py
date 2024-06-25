import argparse
import os
import sys
import re

from typing import List, Set, Pattern
from pathlib import Path
from src.CommonUtils import IOPair, checkFileExistence, clearDirectory, getFileCount, getIOPairs
from src.Exceptions import InvalidOutputNamesCountException


outputDir = Path(sys.path[0]).joinpath("output")


def addSubparser(subparser: argparse.ArgumentParser) -> None:
    subparser.description = "Each line will be checked against all RegEx patterns in the black- and whitelists, and discarded or kept accordingly."
    subparser.epilog = (
        "Each filter contains newline-separated RegEx patterns.\n"
        "If a line in an input file matches at least one of these patterns in a whitelist, it will be kept.\n"
        "If a line in an input file matches at least one of these patterns in a blacklist, it will be discarded.\n"
        "If a line in an input file matches at least one of these patterns in both a whitelist and a blacklist, it will be discarded.\n"
        "\n"
    )

    subparser.add_argument("files", type=str, nargs='+',
                        help="Filepaths to the ssa files, or directories containing them.")
    subparser.add_argument("-d", "--directory", dest="directory", action="store_true",
                        help="Treat the provided input files as directories containing the input files.")
    subparser.add_argument("-n", "--no-delete", dest="delete", action="store_false",
                        help="Don't clear out the output directory.")
    subparser.add_argument("-b", "--blacklist", dest="blacklists", type=str, nargs='+', default=[],
                        help="Filepaths to newline-separated blacklist files.")
    subparser.add_argument("-w", "--whitelist", dest="whitelists", type=str, nargs='+', default=[],
                        help="Filepaths to newline-separated whitelist files.")
    subparser.add_argument("-o", "--output", dest="outputNames", type=str, nargs='+', default=[],
                        help="Output names for each given input, in order.")


def checkArguments(
    files: List[str],
    blacklists: Set[str],
    whitelists: Set[str],
    outputNames: List[str],
    directory: bool,
    delete: bool,
) -> None:
    """Check all arguments for validity."""
    # Check if all files exist
    checkFileExistence(files, directory)
    checkFileExistence(blacklists)
    checkFileExistence(whitelists)

    # Check if there is a bijection between the input files and output names
    fileCount = getFileCount(files, directory)
    if outputNames and len(outputNames) != fileCount:
        raise InvalidOutputNamesCountException(f"The amount {len(outputNames)} of output names does not equal the amount {fileCount} of input files!")


def acceptedByWhitelist(line: str, whitelist: Set[Pattern[str]]) -> bool:
    """Check whether the provided line adheres to the whitelist."""
    return whitelist == set() or next((line for rule in whitelist if rule.search(line)), None) is not None


def acceptedByBlacklist(line: str, blacklist: Set[Pattern[str]]) -> bool:
    """Check whether the provided line adheres to the blacklist."""
    return next((line for rule in blacklist if rule.search(line)), None) is None


def processFilterList(filterPathSet: Set[str]) -> Set[Pattern[str]]:
    """Convert a list of filter files into a list of RegEx Pattern objects."""
    filterFileSet = map(Path, filterPathSet)
    
    filterSet: Set[Pattern[str]] = set()
    for filterFile in filterFileSet:
        with open(filterFile, 'r', encoding="UTF-8") as fileStream:
            for line in fileStream:
                try:
                    filter = re.compile(line.removesuffix('\n'))
                except re.error:
                    print(f"{line} in {filterFile} is not a valid regular expression; ignoring!", file=sys.stderr)
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
    
    with open(ssaFile.input, 'r', encoding="UTF-8") as inputStream:
        with open(ssaFile.output, 'x', encoding="UTF-8") as outputStream:
            for line in filter(
                lambda line: acceptedByWhitelist(line, whitelist) and acceptedByBlacklist(line, blacklist),
                inputStream
            ):
                outputStream.write(line)


def parse(
    files: List[str],
    blacklists: Set[str] = set(),
    whitelists: Set[str] = set(),
    outputNames: List[str] = [],
    directory: bool = False,
    delete: bool = False,
) -> None:
    """Clean up SubStationAlpha files by means of black- and whitelists containing RegEx patterns.

    Args:
        files (List[str]): Filepaths to the ssa files, or directories containing them.
        blacklist (Set[str], optional): Filepaths to newline-separated blacklist files. Defaults to set().
        whitelist (Set[str], optional): Filepaths to newline-separated whitelist files. Defaults to set().
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
    
    IOPairs = getIOPairs(files, outputNames, directory, outputDir)
    whitelist = processFilterList(whitelists)
    blacklist = processFilterList(blacklists)
    
    # Create the output directory
    if not outputDir.is_dir():
        outputDir.mkdir()
    
    if delete:
        clearDirectory(outputDir)
    
    for ssaFile in IOPairs:
        processFile(ssaFile, whitelist, blacklist)
