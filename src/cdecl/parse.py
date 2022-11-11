import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Union


_TYPENAMES = [
    "char",
    "double",
    "float",
    "int",
    "int16_t",
    "int32_t",
    "int64_t",
    "int8_t",
    "long",
    "short",
    "signed",
    "size_t",
    "ssize_t",
    "uint16_t",
    "uint32_t",
    "uint64_t",
    "uint8_t",
    "unsigned",
    "void",
]

_IGNORED_KEYWORDS = [
    "const",
    "extern",
    "inline",
    "register",
    "static",
    "volatile",
]

_KEYWORDS = [
    "typedef",
]


class TokenKind(Enum):
    TK_RESERVED = auto()
    TK_IDENT = auto()
    TK_TYPENAME = auto()
    TK_KEYWORD = auto()


@dataclass
class Token:
    kind: TokenKind
    string: str
    line_num: int
    content_idx: int


class ErrorReporter:
    def __init__(self, content: str):
        self.content = content

    def report_err(self, line_num: int, content_idx: int, err_msg: str):
        line_start_idx = content_idx
        while line_start_idx >= 0 and self.content[line_start_idx] != "\n":
            line_start_idx -= 1
        line_start_idx += 1

        line_end_idx = content_idx
        while line_end_idx < len(self.content) and self.content[line_end_idx] != "\n":
            line_end_idx += 1

        err_line_pos = content_idx - line_start_idx
        err_msg = " " * err_line_pos + "^ " + err_msg

        raise RuntimeError(
            f"Error: {line_num}\n{self.content[line_start_idx:line_end_idx]}\n{err_msg}"
        )


class TypeKind(Enum):
    VOID = auto()
    BOOL = auto()
    CHAR = auto()
    SHORT = auto()
    INT = auto()
    LONG = auto()
    UCHAR = auto()
    USHORT = auto()
    UINT = auto()
    ULONG = auto()
    FLOAT = auto()
    DOUBLE = auto()
    I8 = auto()
    I16 = auto()
    I32 = auto()
    I64 = auto()
    U8 = auto()
    U16 = auto()
    U32 = auto()
    U64 = auto()
    SIZE = auto()
    SSIZE = auto()
    PTR = auto()
    ARR = auto()
    FUNC = auto()


class TypeCounter(Enum):
    CHAR = 0 << 2
    SHORT = 1 << 4
    INT = 1 << 6
    LONG = 1 << 8
    SIGNED = 1 << 10
    UNSIGNED = 1 << 12


@dataclass
class Type:
    kind: TypeKind
    base: Optional["Type"] = None
    ret_ty: Optional["Type"] = None
    params: Optional[list[tuple["Type", Optional[str]]]] = None
    array_len: Optional[Union[int, str]] = None


class Parser:
    _TOK_TO_TYKIND = {
        "void": TypeKind.VOID,
        "bool": TypeKind.BOOL,
        "uint8_t": TypeKind.U8,
        "uint16_t": TypeKind.U16,
        "uint32_t": TypeKind.U32,
        "uint64_t": TypeKind.U64,
        "int8_t": TypeKind.I8,
        "int16_t": TypeKind.I16,
        "int32_t": TypeKind.I32,
        "int64_t": TypeKind.I64,
        "float": TypeKind.FLOAT,
        "double": TypeKind.DOUBLE,
        "size_t": TypeKind.SIZE,
        "ssize_t": TypeKind.SSIZE,
    }

    _TYCNT_TO_TYKIND = {
        TypeCounter.CHAR.value: TypeKind.CHAR,
        TypeCounter.CHAR.value + TypeCounter.SIGNED.value: TypeKind.CHAR,
        TypeCounter.CHAR.value + TypeCounter.UNSIGNED.value: TypeKind.UCHAR,
        TypeCounter.SHORT.value: TypeKind.SHORT,
        TypeCounter.SHORT.value + TypeCounter.INT.value: TypeKind.SHORT,
        TypeCounter.SHORT.value + TypeCounter.SIGNED.value: TypeKind.SHORT,
        TypeCounter.SHORT.value
        + TypeCounter.SIGNED.value
        + TypeCounter.INT.value: TypeKind.SHORT,
        TypeCounter.SHORT.value + TypeCounter.UNSIGNED.value: TypeKind.USHORT,
        TypeCounter.SHORT.value
        + TypeCounter.UNSIGNED.value
        + TypeCounter.INT.value: TypeKind.USHORT,
        TypeCounter.INT.value: TypeKind.INT,
        TypeCounter.SIGNED.value: TypeKind.INT,
        TypeCounter.INT.value + TypeCounter.SIGNED.value: TypeKind.INT,
        TypeCounter.UNSIGNED.value: TypeKind.UINT,
        TypeCounter.INT.value + TypeCounter.UNSIGNED.value: TypeKind.UINT,
        TypeCounter.LONG.value: TypeKind.LONG,
        TypeCounter.LONG.value + TypeCounter.INT.value: TypeKind.LONG,
        TypeCounter.LONG.value + TypeCounter.LONG.value: TypeKind.LONG,
        TypeCounter.LONG.value
        + TypeCounter.LONG.value
        + TypeCounter.INT.value: TypeKind.LONG,
        TypeCounter.LONG.value + TypeCounter.SIGNED.value: TypeKind.LONG,
        TypeCounter.LONG.value
        + TypeCounter.SIGNED.value
        + TypeCounter.INT.value: TypeKind.LONG,
        TypeCounter.LONG.value
        + TypeCounter.SIGNED.value
        + TypeCounter.LONG.value: TypeKind.LONG,
        TypeCounter.LONG.value
        + TypeCounter.SIGNED.value
        + TypeCounter.LONG.value
        + TypeCounter.INT.value: TypeKind.LONG,
        TypeCounter.LONG.value + TypeCounter.UNSIGNED.value: TypeKind.ULONG,
        TypeCounter.LONG.value
        + TypeCounter.UNSIGNED.value
        + TypeCounter.INT.value: TypeKind.ULONG,
        TypeCounter.LONG.value
        + TypeCounter.UNSIGNED.value
        + TypeCounter.LONG.value: TypeKind.ULONG,
        TypeCounter.LONG.value
        + TypeCounter.UNSIGNED.value
        + TypeCounter.LONG.value
        + TypeCounter.INT.value: TypeKind.ULONG,
    }

    def __init__(self, tokens: list[Token], err_rep: ErrorReporter):
        self.tokens = tokens
        self.err_rep = err_rep
        self.idx = 0
        self.typedefs: dict[str, Type] = {}
        self.decls: dict[str, Type] = {}

    def token(self) -> Token:
        return self.tokens[self.idx]

    def next(self) -> "Parser":
        self.idx += 1
        return self

    def get_typedef(self, name: str) -> tuple[bool, Optional[Type]]:
        if name in self.typedefs:
            return True, self.typedefs[name]
        return False, None

    def is_eof(self) -> bool:
        return self.idx >= len(self.tokens)

    def __call__(self) -> dict[str, Type]:
        return self.parse()

    def consume(self, s: str) -> bool:
        if self.token().kind == TokenKind.TK_RESERVED and self.token().string == s:
            self.next()
            return True
        return False

    def expect(self, s: str):
        if not self.consume(s):
            self.err_rep.report_err(
                self.token().line_num, self.token().content_idx, f"expected '{s}'"
            )

    def consume_keyword(self, s: str) -> bool:
        if self.token().kind == TokenKind.TK_KEYWORD and self.token().string == s:
            self.next()
            return True
        return False

    def parse(self) -> dict[str, Type]:
        while not self.is_eof():
            is_typedef = self.consume_keyword("typedef")
            ty = self.declspec()
            if is_typedef:
                self.parse_typedef(ty)
                continue
            self.parse_declarators(ty)
        return self.decls

    def parse_declarators(self, base_ty: Type):
        first = True
        while not self.consume(";"):
            if not first:
                self.expect(",")
            first = False
            start_tok = self.token()
            ty, ident = self.declarator(base_ty, False)
            if ident is None:
                self.err_rep.report_err(
                    start_tok.line_num, start_tok.content_idx, "identifier ommitted"
                )
            assert ident is not None
            self.decls[ident] = ty

    def parse_typedef(self, basety: Type):
        first = True
        while not self.consume(";"):
            if not first:
                self.expect(",")
            first = False
            start_tok = self.token()
            ty, ident = self.declarator(basety, False)
            if ident is None:
                self.err_rep.report_err(
                    start_tok.line_num, start_tok.content_idx, "typedef name ommitted"
                )
            assert ident is not None
            self.typedefs[ident] = ty

    def pointers(self, ty: Type) -> Type:
        while self.consume("*"):
            ty = self.pointer_to(ty)
        return ty

    def pointer_to(self, basety: Type) -> Type:
        return Type(TypeKind.PTR, basety)

    def consume_ident(self) -> Optional[str]:
        ident = None
        if self.token().kind == TokenKind.TK_IDENT:
            ident = self.token().string
            self.next()
        return ident

    def array_of(self, basety: Type, len: Union[int, str]) -> Type:
        return Type(TypeKind.ARR, basety, None, None, len)

    def array_dimensions(self, ty: Type, is_func_param: bool) -> Type:
        array_len = ""
        start_tok = self.token()
        while not self.consume("]"):
            array_len += self.token().string
            self.next()
        if array_len:
            try:
                array_len_int = int(array_len)
                array_len = array_len_int
            except ValueError:
                if not is_func_param:
                    self.err_rep.report_err(
                        start_tok.line_num,
                        start_tok.content_idx,
                        "non-integer-literal array length is not allowed in a non-function-parameter context",
                    )
                pass
        else:
            array_len = 0
        ty = self.type_suffix(ty, is_func_param)
        return self.array_of(ty, array_len)

    def parse_func_ty(self, ret_ty: Type) -> Type:
        fn = Type(TypeKind.FUNC, None, ret_ty, None)
        if self.token().string == "void" and self.tokens[self.idx + 1] == ")":
            self.next().next()
            return fn

        first = True
        fn.params = []
        while not self.consume(")"):
            if not first:
                self.expect(",")
            first = False
            ty = self.declspec()
            start_tok = self.token()
            ty, param_ident = self.declarator(ty, True)
            if ty.kind == TypeKind.ARR:
                assert ty.array_len is not None
                if isinstance(ty.array_len, str):
                    param_match_found = False
                    for param in fn.params:
                        if ty.array_len == param[1]:
                            param_match_found = True
                            break
                    if not param_match_found:
                        self.err_rep.report_err(
                            start_tok.line_num,
                            start_tok.content_idx,
                            "non-integer-literal array length does not match any preceding function parameter name",
                        )
            fn.params.append((ty, param_ident))

        return fn

    def type_suffix(self, ty: Type, is_func_param: bool) -> Type:
        if self.consume("("):
            return self.parse_func_ty(ty)
        if self.consume("["):
            return self.array_dimensions(ty, is_func_param)
        return ty

    def declarator(self, ty: Type, is_func_param: bool) -> tuple[Type, Optional[str]]:
        ty = self.pointers(ty)
        ident = None
        super_ty = None

        if self.consume("("):
            super_ty, ident = self.declarator(Type(TypeKind.INT), is_func_param)
            self.expect(")")

        if ident is None:
            ident = self.consume_ident()
        ty = self.type_suffix(ty, is_func_param)

        if super_ty is not None:
            this_ty = super_ty
            while True:
                if this_ty.kind in [TypeKind.ARR, TypeKind.PTR]:
                    assert this_ty.base is not None
                    if this_ty.base.kind in [TypeKind.ARR, TypeKind.PTR, TypeKind.FUNC]:
                        this_ty = this_ty.base
                        continue
                    break
                if this_ty.kind == TypeKind.FUNC:
                    assert this_ty.ret_ty is not None
                    if this_ty.ret_ty.kind in [
                        TypeKind.ARR,
                        TypeKind.PTR,
                        TypeKind.FUNC,
                    ]:
                        this_ty = this_ty.ret_ty
                        continue
                    break
                assert False

            if this_ty.kind == TypeKind.FUNC:
                this_ty.ret_ty = ty
            else:
                this_ty.base = ty
            ty = super_ty

        return ty, ident

    def declspec(self) -> Type:
        start_tok = self.token()
        type_counter = 0
        ty_kind = TypeKind.INT

        extant_tydef_found, ty = self.get_typedef(self.token().string)
        if extant_tydef_found:
            self.next()
            assert ty is not None
            return ty

        if self.token().kind != TokenKind.TK_TYPENAME:
            self.err_rep.report_err(
                self.token().line_num, self.token().content_idx, "unrecognised typename"
            )

        while self.token().kind == TokenKind.TK_TYPENAME:
            token = self.token()
            self.next()

            if token.string in Parser._TOK_TO_TYKIND:
                return Type(Parser._TOK_TO_TYKIND[token.string])

            if token.string == "char":
                type_counter += TypeCounter.CHAR.value
            elif token.string == "short":
                type_counter += TypeCounter.SHORT.value
            elif token.string == "int":
                type_counter += TypeCounter.INT.value
            elif token.string == "long":
                type_counter += TypeCounter.LONG.value
            elif token.string == "signed":
                type_counter += TypeCounter.SIGNED.value
            elif token.string == "unsigned":
                type_counter += TypeCounter.UNSIGNED.value
            else:
                assert False

            if type_counter not in Parser._TYCNT_TO_TYKIND:
                self.err_rep.report_err(
                    start_tok.line_num,
                    start_tok.content_idx,
                    "invalid combination of typenames",
                )

            ty_kind = Parser._TYCNT_TO_TYKIND[type_counter]

        return Type(ty_kind)


def _pre_process(content: str) -> str:
    content = re.sub(
        r"\[\s*(?:/\*)*\s*([a-zA-Z0-9_]+)\s*(?:\*/)*\s*\]", r"[\1]", content
    )

    content = re.sub(r"/\*.*?\*/", "", content, flags=re.S)
    content = re.sub(r"//.*$", "", content, flags=re.M)
    content = re.sub(r"(?:typedef)\s*enum.*?{.*?}.*?;", "", content, flags=re.S)

    pattern = re.compile(
        r"#define\s+([a-zA-Z0-9_]+)\s+([(]*[0-9]+[x0-9 */+-<>|&%=()]*)\s*"
    )
    match = pattern.search(content)
    while match:
        line = match.group(0)
        content = re.sub(re.escape(line), "", content)
        ident = match.group(1)
        val = match.group(2)
        if all([x in "0123456789 */+-<>|&%=()" for x in val]):
            val = str(eval(val))
        content = re.sub(ident, val, content)
        match = pattern.search(content)

    content = re.sub(r"^\s*#.*$", "", content, flags=re.M)
    content = re.sub(r'^\s*extern "C".*$', "", content, flags=re.M)
    content = re.sub(r"^}\s*$", "", content, flags=re.M)
    content = re.sub(r"\s+$", "", content, flags=re.M)
    return content


def _is_ident_char(c: str) -> bool:
    return c.isalpha() or c.isdigit() or c == "_"


def _tokenise(content: str, err_rep: ErrorReporter) -> list[Token]:
    line_num = 1
    tokens = []
    i = 0
    while i < len(content):
        c = content[i]
        if c.isspace():
            if c == "\n":
                line_num += 1
            i += 1
            continue
        if c in "*();{},[]":
            tokens.append(Token(TokenKind.TK_RESERVED, c, line_num, i))
            i += 1
            continue
        if _is_ident_char(c):
            w = ""
            start_idx = i
            while _is_ident_char(c):
                w += c
                i += 1
                c = content[i]
            if w in _IGNORED_KEYWORDS:
                continue
            if w in _KEYWORDS:
                tokens.append(Token(TokenKind.TK_KEYWORD, w, line_num, start_idx))
                continue
            if w in _TYPENAMES:
                tokens.append(Token(TokenKind.TK_TYPENAME, w, line_num, start_idx))
                continue
            tokens.append(Token(TokenKind.TK_IDENT, w, line_num, start_idx))
            continue
        err_rep.report_err(line_num, i, "unexpected token")
    return tokens


def _parse_tokens(tokens: list[Token], err_rep: ErrorReporter) -> dict[str, Type]:
    parser = Parser(tokens, err_rep)
    return parser()


def parse_decls(decl_strs: list[str]) -> dict[str, Type]:
    decls = {}
    for decl_str in decl_strs:
        err_rep = ErrorReporter(decl_str)
        decl_str = _pre_process(decl_str)
        try:
            tokens = _tokenise(decl_str, err_rep)
            decls |= _parse_tokens(tokens, err_rep)
        except RuntimeError as e:
            print(e)
    return decls
