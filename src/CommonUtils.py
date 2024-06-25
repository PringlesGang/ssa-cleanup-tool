import os
from pathlib import Path
from typing import Any, Iterable, List, NamedTuple, Set

from src.Exceptions import NotAFileException


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


def checkFileExistence(pathStrings: Iterable[str], directory: bool = False) -> None:
    """Check if all files exist, or directories if the boolean is set."""
    paths = list(map(Path, pathStrings))

    if directory:
        nonexistentDirectory = next((directory for directory in paths if not directory.is_dir()), None)
        if nonexistentDirectory is not None:
            raise NotADirectoryError(f"{nonexistentDirectory} is not a directory!")
    else:
        nonexistentFile = next((file for file in paths if not file.is_file()), None)
        if nonexistentFile is not None:
            raise NotAFileException(f"{nonexistentFile} is not a file!")


def getInputPaths(
    files: List[str],
    directory: bool,
) -> List[Path]:
    """Convert the input files list into a list of Paths, and coalless the directories if necessary."""
    inputPaths = list(map(Path, files))
    if directory:
        inputPaths = getFilesInDirectories(inputPaths)
                
    return inputPaths


def clearDirectory(directory: Path):
    """Deletes all files in a directory."""
    for file in [file for file in directory.iterdir() if file.is_file()]:
        os.remove(file)


def getIOPairs(
    files: List[str],
    output: List[str],
    directory: bool,
    outputDir: Path
) -> Set[IOPair]:
    """Pair up the input paths with the corresponding output paths."""
    inputPaths = getInputPaths(files, directory)
    
    return set(
        map( # Map to IOPair
            lambda pair: IOPair(pair[0], pair[1]),
            zip( # Pair up input files and output files
                inputPaths,
                # Use output paths if provided; otherwise use input names
                list(map(Path, output)) if output else list(map(lambda file: outputDir.joinpath(Path(file).name), inputPaths)))
            )
        )
