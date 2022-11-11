import argparse

from cdecl.parse import parse_decls
from cdecl.print import print_decls


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Parse c declarations.",
    )
    parser.add_argument(
        "decl_strs",
        type=str,
        help="A list of c declarations to be parsed.",
        nargs="+",
    )
    args = parser.parse_args()
    decl_strs = args.decl_strs
    decls = parse_decls(decl_strs)
    print_decls(decls)
