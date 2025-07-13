import py_compile


def test_debug_harvester_compiles():
    py_compile.compile("debug_harvester.py", doraise=True)
