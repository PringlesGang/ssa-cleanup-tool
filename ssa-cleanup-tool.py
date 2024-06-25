#!/usr/bin/env python3.12

import argparse
import sys

import src.RegexParser as RegexParser
import src.SectionReplacer as SectionReplacer


def getParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="General tools for cleaning up SubStationAlpha files.")

    subparsers = parser.add_subparsers(title="tool", dest="subcommand", required=True,
        help="The tool to run.")
    RegexParser.addSubparser(subparsers.add_parser("parse-regex", aliases=["regex"], add_help=True, formatter_class=argparse.RawTextHelpFormatter,
        help="Reduce ssa files according to black- and whitelists of RegEx patterns."))
    SectionReplacer.addSubparser(subparsers.add_parser("replace-sections", aliases=["section"], add_help=True, formatter_class=argparse.RawTextHelpFormatter,
        help="Replace entire sections with custom ones according to template files."))
    
    return parser


def controlFlow(args: argparse.Namespace):
    match args.subcommand.lower():
        case "parse-regex" | "regex":
            RegexParser.parse(
                args.files,
                args.blacklists,
                args.whitelists,
                args.outputNames,
                args.directory,
                args.delete,
            )
        case "replace-sections" | "section":
            SectionReplacer.replaceSections(
                args.files,
                args.templates,
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