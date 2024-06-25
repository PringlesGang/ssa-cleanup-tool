import argparse
import os
from pathlib import Path
import re
import sys
from typing import List, Set

from src.CommonUtils import IOPair, checkFileExistence, clearDirectory, getIOPairs
from src.Exceptions import InvalidOutputCountException


outputDir = Path(sys.path[0]).joinpath("output")

# Line consisting of a string enclosed in square brackets
# To denote _removing_ the section, prepend '~'
sectionPattern = re.compile("^\s*~?\[.*\]\s*$")


def addSubparser(subparser: argparse.ArgumentParser) -> None:
    subparser.description = "Replaces entire sections of ssa files with predefined templates."
    subparser.epilog = (
        "The format of the template files is as any other ssa file; section labels are enclosed in [square brackets].\n"
        "Everything between that label and the next (or the end of the file) will replace what's in the given input files.\n"
        "\n"
        "To remove a section outright, prepend a '~' to the section label in the template, like so: ~[Section Label]\n"
        "\n"
    )

    subparser.add_argument("files", type=str, nargs='+',
                           help="Filepaths to the ssa files, or directories containing them.")
    subparser.add_argument("-d", "--directory", dest="directory", action="store_true",
                           help="Treat the provided input files as directories containing the input files.")
    subparser.add_argument("-n", "--no-delete", dest="delete", action="store_false",
                           help="Don't clear out the output directory.")
    subparser.add_argument("-t", "--templates", dest="templates", type=str, nargs='+',
                           help="Filepaths to the template files, dictating the text under what sections should be replaced with what.")
    subparser.add_argument("-o", "--output", dest="output", type=str, nargs='+', default=[],
                           help="Output paths for each given input, in order.")


def checkArguments(
    files: List[str],
    templates: Set[str],
    output: List[str],
    directory: bool,
    delete: bool,
) -> None:
    """Check all arguments for validity."""
    checkFileExistence(files, directory)
    checkFileExistence(templates)

    # Check if there is a bijection between the input and output paths
    if output and len(output) != len(files):
        raise InvalidOutputCountException(f"The amount {len(output)} of output paths does not equal the amount {len(files)} of input files!")
    checkFileExistence(list(map(lambda path: str(Path(path).parent.absolute()), output)), True)


def processTemplateList(templates: Set[str]) -> tuple[dict[str, list[str]], set[str]]:
    """Compile the list of template files into a dictionary mapping sections to their replacement text, and a set of sections to remove."""
    templatePaths = map(Path, templates)
    mapping: dict[str, list[str]] = dict()
    removeSections: set[str] = set()

    for templateFile in templatePaths:
        with open(templateFile, 'r', encoding="UTF-8-sig") as fileStream:
            section = ""
            text: list[str] = list()

            for line in fileStream:
                line = line.removesuffix('\n')
                if sectionPattern.fullmatch(line):
                    if section != "":
                        if section[0] != '~':
                            mapping[section] = text
                        else:
                            removeSections.add(section[1:])

                    section = line
                    text = list()
                else:
                    text += [line]
            
            if section != "":
                if section[0] != '~':
                    mapping[section] = text
                else:
                    removeSections.add(section[1:])

    return (mapping, removeSections)


def processFile(ssaFile: IOPair, sectionToTemplateMap: dict[str, list[str]], removeSections: set[str]) -> None:
    """Apply the template files to the given IOPair."""
    if ssaFile.output.exists():
        os.remove(ssaFile.output)

    with open(ssaFile.input, 'r', encoding="UTF-8-sig") as inputStream:
        with open(ssaFile.output, 'x', encoding="UTF-8-sig") as outputStream:
            skipSection = False
            for line in inputStream:
                line = line.removesuffix('\n')
                if sectionPattern.fullmatch(line): # Start of new section
                    sectionTemplated = line in set(sectionToTemplateMap.keys())
                    removeSection = line in removeSections
                    skipSection = sectionTemplated | removeSection

                    if not removeSection:
                        outputStream.write(line + '\n')
                    if sectionTemplated:
                        for templateLine in sectionToTemplateMap[line]:
                            outputStream.write(templateLine + '\n')
                elif not skipSection: # Section not templated
                    outputStream.write(line + '\n')
                # If templated; don't write


def replaceSections(
    files: List[str],
    templates: Set[str],
    output: List[str] = [],
    directory: bool = False,
    delete: bool = False,
) -> None:
    """Replace entire sections of SubStationAlpha files with predefined text.
    
    Args:
        files (List[str]): Filepaths to the ssa files, or directories containing them.
        templates (Set[str]): Filepaths to the template files denoting what sections to overwrite with what, or what sections to remove outright.
        output (List[str], optional): Output paths for each given input, in order. Defaults to [].
        directory (bool, optional): Set to True if the `files` argument consists of directories. Defaults to False.
        delete (bool, optional): Set to True if you want the program to clear the output directory first. Defaults to False.
    """
    checkArguments(
        files,
        templates,
        output,
        directory,
        delete
    )

    IOPairs = getIOPairs(files, output, directory, outputDir)
    (sectionToTemplateMap, removeSections) = processTemplateList(templates)

    # Create the output directory
    if not outputDir.is_dir():
        outputDir.mkdir()

    if delete:
        clearDirectory(outputDir)

    for ssaFile in IOPairs:
        processFile(ssaFile, sectionToTemplateMap, removeSections)