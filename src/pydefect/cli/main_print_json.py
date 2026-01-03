# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""pydefect_print CLI entry point.

Simple utility to print contents of JSON/YAML files.

Example:
    $ pydefect_print calc_results.json
    $ pydefect_print repr calc_results.json supercell_info.json
"""

import sys
from monty.serialization import loadfn


def main():
    """Entry point for pydefect_print CLI."""
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: pydefect_print [repr] <file1> [file2] ...")
        print("")
        print("Print contents of JSON/YAML files.")
        print("")
        print("Options:")
        print("  repr    Use __repr__ instead of __str__")
        print("  -h, --help  Show this message")
        return

    if sys.argv[1] == "repr":
        filenames = sys.argv[2:]
        use_repr = True
    else:
        filenames = sys.argv[1:]
        use_repr = False

    for filename in filenames:
        print("-" * 80)
        print(f"file: {filename}")
        obj = loadfn(filename)
        if use_repr:
            print(obj.__repr__())
        else:
            print(obj.__str__())


if __name__ == "__main__":
    main()
