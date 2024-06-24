#!/usr/bin/env python3.12

import argparse
import sys

import src.RegexParser as RegexParser


def getParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="General tools for cleaning up SubStationAlpha files.")

    subparsers = parser.add_subparsers(title="tool", dest="subcommand", required=True,
                                       help="The tool to run.")
    RegexParser.addSubparser(subparsers.add_parser("regex", add_help=True,
                                                   help="Reduce ssa files according to black- and whitelists of RegEx patterns."))
    
    return parser


def controlFlow(args: argparse.Namespace):
    match args.subcommand.lower():
        case "regex":
            RegexParser.parse(
                args.files,
                args.blacklists,
                args.whitelists,
                args.outputNames,
                args.directory,
                args.delete,
            )


def parseArguments() -> argparse.Namespace:
    """Parse the command-line arguments passed into the program."""
    return getParser().parse_args()


if __name__ == "__main__":
    try:
        args = parseArguments()
        controlFlow(args)
    except Exception as e:
        print(e, file=sys.stderr)
        exit(1)