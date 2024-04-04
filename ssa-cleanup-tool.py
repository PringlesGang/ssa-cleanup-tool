import argparse
import os
import sys
import re

from typing import Any, Tuple, List, Set, Pattern
from pathlib import Path


def flattenOnce(iterable: List[List[Any]]) -> List[Any]:
    return [item for item in [deepIterable for deepIterable in iterable]]


def acceptedByWhitelist(line: str, whitelist: Set[Pattern[str]]) -> bool:
    return True in [(rule.match(line) is not None) for rule in whitelist]


def acceptedByBlacklist(line: str, blacklist: Set[Pattern[str]]) -> bool:
    return True not in [(rule.match(line) is not None) for rule in blacklist]


def getFilesInDirectories(directories: List[Path]) -> List[Path]:
    files: List[Path] = []

    for directory in directories:
        files += [file for file in directory.iterdir() if file.is_file()]
    
    return files


def processFilterList(filterPathList: List[str]) -> Set[Pattern[str]]:
    filterFileList = [Path(path) for path in filterPathList]
    
    filterSet: set[re.Pattern[str]] = set()
    for filterFile in filterFileList:
            fileStream = open(filterFile, 'r')
            
            for line in fileStream:
                try:
                    filter = re.compile(line)
                except re.error:
                    print(f"{line} in {filterFile} is not a valid regular expression; ignoring.", file=sys.stderr)
                else:
                    filterSet.add(filter)
            
            fileStream.close()
    
    return filterSet

def processFile(
    ssaFile: Tuple[Path, Path],
    whitelist: Set[Pattern[str]],
    blacklist: Set[Pattern[str]],
) -> None:
    input = ssaFile[0]
    output = ssaFile[1]

    if output.exists():
        os.remove(output)
    
    inputStream = open(input, 'r', encoding="UTF-8-sig")
    outputStream = open(output, 'x')

    for line in inputStream:
        if acceptedByWhitelist(line, whitelist) and acceptedByBlacklist(line, blacklist):
            outputStream.write(line)
        
    inputStream.close()
    outputStream.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up SubStationAlpha files.")
    parser.add_argument("files", type=str, nargs='+',
                        help="Paths to the files to operate on")
    parser.add_argument("-d", "--directory", dest="directory", action="store_true",
                        help="Input paths are directories. All files within will be taken as input.")
    parser.add_argument("-n", "--no-delete", dest="delete", action="store_false",
                        help="Don't delete the files currently in the output folder.")
    parser.add_argument("-b", "--blacklist", dest="blacklists", type=str, nargs='+', default=[],
                        help="List of newline-separated blacklists describing what RegEx-matched lines to skip.")
    parser.add_argument("-w", "--whitelist", dest="whitelists", type=str, nargs='+', default=[],
                        help="List of newline-separated whitelists describing what RegEx-matched lines to keep.")
    parser.add_argument("-o", "--output", dest="outputNames", type=str, nargs='+', default=[],
                        help="Output names for each given input.")
    args = parser.parse_args()

    if args.outputNames and args.outputNames.len() != args.files.len():
        print("The amount of output names does not match the amount of input files.")
        exit(1)
    
    # Check if all files provided exist
    allFiles = args.files + args.blacklists + args.whitelists
    for file in allFiles:
        if not Path(file).exists():
            print(f"{file} does not exist.", file=sys.stderr)
            exit(1)
    
    inputPaths = [Path(file) for file in args.files]
    whitelist = processFilterList(args.whitelists)
    blacklist = processFilterList(args.blacklists)
    
    if args.directory:
        for directory in inputPaths:
            if not Path(directory).is_dir():
                print(f"{directory} is not a directory.", file=sys.stderr)
                exit(1)
        inputPaths = getFilesInDirectories(inputPaths)
    else:
        for file in inputPaths:
            if not Path(file).is_file():
                print(f"{file} is not a file.", file=sys.stderr)
                exit(1)
    
    # If no output names are given, use the names of the input
    outputNames = args.outputNames if args.outputNames else [Path(file).name for file in inputPaths]
    outputPaths = [Path("./output").joinpath(name) for name in outputNames]

    processFiles = zip(inputPaths, outputPaths)

    # Create the output directory
    if not Path("./output").is_dir():
        Path("./output").mkdir()
    
    if args.delete:
        for file in [file for file in Path("./output").iterdir() if file.is_file()]:
            os.remove(file)
    
    for ssaFile in processFiles:
        processFile(ssaFile, whitelist, blacklist)
