from cdecl.parse import Type


def print_decls(decls: dict[str, Type]):
    for ident, ty in decls.items():
        print(ident)
        print(ty)
