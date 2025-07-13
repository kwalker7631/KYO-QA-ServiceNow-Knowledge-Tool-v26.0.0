import py_compile


def test_data_harvesters_py_compile():
    py_compile.compile("data_harvesters.py", doraise=True)
