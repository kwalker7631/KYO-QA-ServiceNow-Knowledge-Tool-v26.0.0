import sys
from types import SimpleNamespace

_SAVED_WORKBOOKS = {}


class Cell:
    def __init__(self, sheet, row, column):
        self._sheet = sheet
        self._row = row
        self._col = column

    @property
    def value(self):
        r = self._row - 1
        c = self._col - 1
        if r < len(self._sheet._rows) and c < len(self._sheet._rows[r]):
            return self._sheet._rows[r][c]
        return None

    @value.setter
    def value(self, val):
        r = self._row - 1
        c = self._col - 1
        while len(self._sheet._rows) <= r:
            self._sheet._rows.append([])
        row = self._sheet._rows[r]
        while len(row) <= c:
            row.append(None)
        row[c] = val


class DummySheet:
    def __init__(self):
        self._rows = []

    def append(self, row):
        self._rows.append(list(row))

    def cell(self, row, column):
        return Cell(self, row, column)

    def __getitem__(self, index):
        idx = index - 1
        if idx >= len(self._rows):
            return []
        return [SimpleNamespace(value=v) for v in self._rows[idx]]

    def iter_cols(self, min_col=None, max_col=None, min_row=1):
        max_row = len(self._rows)
        for row in range(min_row, max_row + 1):
            val = None
            if row - 1 < len(self._rows) and min_col - 1 < len(self._rows[row - 1]):
                val = self._rows[row - 1][min_col - 1]
            yield SimpleNamespace(value=val)


class DummyWorkbook:
    def __init__(self):
        self.active = DummySheet()

    def save(self, path):
        _SAVED_WORKBOOKS[str(path)] = [row[:] for row in self.active._rows]
        with open(path, "w", encoding="utf-8") as f:
            f.write("dummy")


def load_workbook(path):
    wb = DummyWorkbook()
    wb.active._rows = [row[:] for row in _SAVED_WORKBOOKS.get(str(path), [])]
    return wb


def ensure_openpyxl_stub():
    if "openpyxl" not in sys.modules:
        sys.modules["openpyxl"] = SimpleNamespace(
            Workbook=DummyWorkbook, load_workbook=load_workbook
        )
