from pytest import raises

from cdecl.parse import (
    _pre_process,
    _tokenise,
    _parse_tokens,
    TypeKind,
    ErrorReporter,
)


def test_parse():
    content = "int a;"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.INT
    assert decls["a"].base is None
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int *p;"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "p" in decls
    assert decls["p"].kind == TypeKind.PTR
    assert decls["p"].base is not None
    assert decls["p"].base.kind == TypeKind.INT
    assert decls["p"].params is None
    assert decls["p"].ret_ty is None

    content = "int a[];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.ARR
    assert decls["a"].base is not None
    assert decls["a"].base.kind == TypeKind.INT
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int *a[];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.ARR
    assert decls["a"].base is not None
    assert decls["a"].base.kind == TypeKind.PTR
    assert decls["a"].base.base is not None
    assert decls["a"].base.base.kind == TypeKind.INT
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int (*a)[];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.PTR
    assert decls["a"].base is not None
    assert decls["a"].base.kind == TypeKind.ARR
    assert decls["a"].base.base is not None
    assert decls["a"].base.base.kind == TypeKind.INT
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int a[][];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.ARR
    assert decls["a"].base is not None
    assert decls["a"].base.kind == TypeKind.ARR
    assert decls["a"].base.base is not None
    assert decls["a"].base.base.kind == TypeKind.INT
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int (*a[])[];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.ARR
    assert decls["a"].base is not None
    assert decls["a"].base.kind == TypeKind.PTR
    assert decls["a"].base.base is not None
    assert decls["a"].base.base.kind == TypeKind.ARR
    assert decls["a"].base.base.base is not None
    assert decls["a"].base.base.base.kind == TypeKind.INT
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int foo(void);"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "foo" in decls
    assert decls["foo"].kind == TypeKind.FUNC
    assert decls["foo"].base is None
    assert decls["foo"].params is not None
    assert len(decls["foo"].params) == 1
    assert decls["foo"].params[0][0].kind == TypeKind.VOID
    assert decls["foo"].params[0][1] is None
    assert decls["foo"].ret_ty is not None
    assert decls["foo"].ret_ty.kind == TypeKind.INT

    content = "int foo(char c, long l);"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "foo" in decls
    assert decls["foo"].kind == TypeKind.FUNC
    assert decls["foo"].base is None
    assert decls["foo"].params is not None
    assert len(decls["foo"].params) == 2
    assert decls["foo"].params[0][0].kind == TypeKind.CHAR
    assert decls["foo"].params[0][1] == "c"
    assert decls["foo"].params[1][0].kind == TypeKind.LONG
    assert decls["foo"].params[1][1] == "l"
    assert decls["foo"].ret_ty is not None
    assert decls["foo"].ret_ty.kind == TypeKind.INT

    content = "int (*pf)(short s, uint64_t u);"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "pf" in decls
    assert decls["pf"].kind == TypeKind.PTR
    assert decls["pf"].base is not None
    assert decls["pf"].base.kind == TypeKind.FUNC
    assert decls["pf"].base.params is not None
    assert len(decls["pf"].base.params) == 2
    assert decls["pf"].base.params[0][0].kind == TypeKind.SHORT
    assert decls["pf"].base.params[0][1] == "s"
    assert decls["pf"].base.params[1][0].kind == TypeKind.U64
    assert decls["pf"].base.params[1][1] == "u"
    assert decls["pf"].base.ret_ty is not None
    assert decls["pf"].base.ret_ty.kind == TypeKind.INT

    content = "int (*(*pf)(double d))[3];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "pf" in decls
    assert decls["pf"].kind == TypeKind.PTR
    assert decls["pf"].base is not None
    assert decls["pf"].base.kind == TypeKind.FUNC
    assert decls["pf"].base.params is not None
    assert len(decls["pf"].base.params) == 1
    assert decls["pf"].base.params[0][0].kind == TypeKind.DOUBLE
    assert decls["pf"].base.params[0][1] == "d"
    assert decls["pf"].base.ret_ty is not None
    assert decls["pf"].base.ret_ty.kind == TypeKind.PTR
    assert decls["pf"].base.ret_ty.base is not None
    assert decls["pf"].base.ret_ty.base.kind == TypeKind.ARR
    assert decls["pf"].base.ret_ty.base.base is not None
    assert decls["pf"].base.ret_ty.base.base.kind == TypeKind.INT

    content = "int a, *p, arr[], *arrp[], (*parr)[], aarr[][], (*arrparr[])[];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 7
    assert "a" in decls
    assert decls["a"].kind == TypeKind.INT
    assert decls["a"].base is None
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None
    assert "p" in decls
    assert decls["p"].kind == TypeKind.PTR
    assert decls["p"].base is not None
    assert decls["p"].base.kind == TypeKind.INT
    assert decls["p"].params is None
    assert decls["p"].ret_ty is None
    assert "arr" in decls
    assert decls["arr"].kind == TypeKind.ARR
    assert decls["arr"].base is not None
    assert decls["arr"].base.kind == TypeKind.INT
    assert decls["arr"].params is None
    assert decls["arr"].ret_ty is None
    assert "arrp" in decls
    assert decls["arrp"].kind == TypeKind.ARR
    assert decls["arrp"].base is not None
    assert decls["arrp"].base.kind == TypeKind.PTR
    assert decls["arrp"].base.base is not None
    assert decls["arrp"].base.base.kind == TypeKind.INT
    assert decls["arrp"].params is None
    assert decls["arrp"].ret_ty is None
    assert "parr" in decls
    assert decls["parr"].kind == TypeKind.PTR
    assert decls["parr"].base is not None
    assert decls["parr"].base.kind == TypeKind.ARR
    assert decls["parr"].base.base is not None
    assert decls["parr"].base.base.kind == TypeKind.INT
    assert decls["parr"].params is None
    assert decls["parr"].ret_ty is None
    assert "aarr" in decls
    assert decls["aarr"].kind == TypeKind.ARR
    assert decls["aarr"].base is not None
    assert decls["aarr"].base.kind == TypeKind.ARR
    assert decls["aarr"].base.base is not None
    assert decls["aarr"].base.base.kind == TypeKind.INT
    assert decls["aarr"].params is None
    assert decls["aarr"].ret_ty is None
    assert "arrparr" in decls
    assert decls["arrparr"].kind == TypeKind.ARR
    assert decls["arrparr"].base is not None
    assert decls["arrparr"].base.kind == TypeKind.PTR
    assert decls["arrparr"].base.base is not None
    assert decls["arrparr"].base.base.kind == TypeKind.ARR
    assert decls["arrparr"].base.base.base is not None
    assert decls["arrparr"].base.base.base.kind == TypeKind.INT
    assert decls["arrparr"].params is None
    assert decls["arrparr"].ret_ty is None

    content = """\
    typedef int (*func_t)(char c, long l);
    int foo(func_t pf, int i);
    """
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "foo" in decls
    assert decls["foo"].kind == TypeKind.FUNC
    assert decls["foo"].base is None
    assert decls["foo"].params is not None
    assert len(decls["foo"].params) == 2
    assert decls["foo"].params[0][0].kind == TypeKind.PTR
    assert decls["foo"].params[0][0].base is not None
    assert decls["foo"].params[0][0].base.kind == TypeKind.FUNC
    assert decls["foo"].params[0][0].base.ret_ty is not None
    assert decls["foo"].params[0][0].base.ret_ty.kind == TypeKind.INT
    assert decls["foo"].params[0][0].base.params is not None
    assert len(decls["foo"].params[0][0].base.params) == 2
    assert decls["foo"].params[0][0].base.params[0][0].kind == TypeKind.CHAR
    assert decls["foo"].params[0][0].base.params[0][1] == "c"
    assert decls["foo"].params[0][0].base.params[1][0].kind == TypeKind.LONG
    assert decls["foo"].params[0][0].base.params[1][1] == "l"
    assert decls["foo"].params[0][1] == "pf"
    assert decls["foo"].params[1][0].kind == TypeKind.INT
    assert decls["foo"].params[1][1] == "i"
    assert decls["foo"].ret_ty is not None
    assert decls["foo"].ret_ty.kind == TypeKind.INT

    content = "unsigned int a;"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.UINT
    assert decls["a"].base is None
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "unsigned long long int a;"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.ULONG
    assert decls["a"].base is None
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "unsigned short int a;"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.USHORT
    assert decls["a"].base is None
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None


def test_parse_errs():
    content = "int a = 1;"
    err_rep = ErrorReporter(content)
    with raises(RuntimeError):
        tokens = _tokenise(content, err_rep)

    content = """\
    int a;
    int *p;
    int arr[];
    unsigned short long int b;
    """
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    with raises(RuntimeError):
        _parse_tokens(tokens, err_rep)

    content = """\
    int a;
    int *p;
    int arr[];
    int b c;
    """
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    with raises(RuntimeError):
        _parse_tokens(tokens, err_rep)

    content = """\
    int a;
    int *p;
    int arr[];
    int (*)(char c);
    """
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    with raises(RuntimeError):
        _parse_tokens(tokens, err_rep)

    content = """\
    int a;
    int *p;
    int arr[];
    typedef int (*)(char c);
    """
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    with raises(RuntimeError):
        _parse_tokens(tokens, err_rep)

    content = """\
    int a;
    int *p;
    int arr[];
    my_special_t b;
    """
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    with raises(RuntimeError):
        _parse_tokens(tokens, err_rep)

    content = "int a[ags];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    with raises(RuntimeError):
        _parse_tokens(tokens, err_rep)

    content = "int foo(size_t sz, int data[abc]);"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    with raises(RuntimeError):
        _parse_tokens(tokens, err_rep)


def test_parse_array_len():
    content = "int a[3];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.ARR
    assert decls["a"].array_len is not None
    assert decls["a"].array_len == 3
    assert decls["a"].base is not None
    assert decls["a"].base.kind == TypeKind.INT
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int a[3][4];"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "a" in decls
    assert decls["a"].kind == TypeKind.ARR
    assert decls["a"].array_len is not None
    assert decls["a"].array_len == 3
    assert decls["a"].base is not None
    assert decls["a"].base.kind == TypeKind.ARR
    assert decls["a"].base.array_len is not None
    assert decls["a"].base.array_len == 4
    assert decls["a"].base.base is not None
    assert decls["a"].base.base.kind == TypeKind.INT
    assert decls["a"].params is None
    assert decls["a"].ret_ty is None

    content = "int foo(size_t sz, int data[sz]);"
    err_rep = ErrorReporter(content)
    tokens = _tokenise(content, err_rep)
    decls = _parse_tokens(tokens, err_rep)
    assert len(decls) == 1
    assert "foo" in decls
    assert decls["foo"].kind == TypeKind.FUNC
    assert decls["foo"].base is None
    assert decls["foo"].params is not None
    assert len(decls["foo"].params) == 2
    assert decls["foo"].params[0][0].kind == TypeKind.SIZE
    assert decls["foo"].params[0][1] == "sz"
    assert decls["foo"].params[1][0].kind == TypeKind.ARR
    assert decls["foo"].params[1][0].array_len == "sz"
    assert decls["foo"].params[1][1] == "data"
    assert decls["foo"].params[1][0].base is not None
    assert decls["foo"].params[1][0].base.kind == TypeKind.INT
    assert decls["foo"].ret_ty is not None
    assert decls["foo"].ret_ty.kind == TypeKind.INT


def test_pre_process():
    content = "int foo(size_t sz, int src[/*sz*/], int dst[ /* sz */ ]);"
    content = _pre_process(content)
    assert content == "int foo(size_t sz, int src[sz], int dst[sz]);"

    content = """\
    //test
    #define ARR_LEN 3
    #define DATA_LEN 5
    #define DERIVED (ARR_LEN * DATA_LEN)
    int foo(int src[ARR_LEN], int dst[/*ARR_LEN*/]);
    int bar(int data[DATA_LEN]);
    int baz(int arr[DERIVED]);
    """
    content = _pre_process(content)
    assert (
        content
        == "\n    int foo(int src[3], int dst[3]);\n    int bar(int data[5]);\n    int baz(int arr[15]);"
    )

    content = """\
    //test
    int foo(int i);
    typedef enum {
        ONE = 1,
        TWO = 2,
    } my_enum_t;
    int bar(int i);
    """
    content = _pre_process(content)
    assert content == "\n    int foo(int i);\n    int bar(int i);"
