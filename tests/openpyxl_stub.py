import sys
import json
from types import SimpleNamespace


class Cell:
    def __init__(self, worksheet, row, column):
        self._ws = worksheet
        self._row = row - 1
        self._col = column - 1

    @property
    def value(self):
        try:
            return self._ws._rows[self._row][self._col]
        except IndexError:
            return None

    @value.setter
    def value(self, val):
        while len(self._ws._rows) <= self._row:
            self._ws._rows.append([])
        while len(self._ws._rows[self._row]) <= self._col:
            self._ws._rows[self._row].append(None)
        self._ws._rows[self._row][self._col] = val


class Worksheet:
    def __init__(self, rows=None):
        self._rows = rows or []

    def append(self, row):
        self._rows.append(list(row))

    def __getitem__(self, idx):
        row = self._rows[idx - 1]
        return [SimpleNamespace(value=v) for v in row]

    def iter_cols(self, min_col, max_col, min_row=1):
        for r in range(min_row - 1, len(self._rows)):
            for col in range(min_col - 1, max_col):
                yield SimpleNamespace(
                    value=(self._rows[r][col] if col < len(self._rows[r]) else None)
                )

    def cell(self, row, column):
        return Cell(self, row, column)


class Workbook:
    def __init__(self, rows=None):
        self.active = Worksheet(rows)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.active._rows, f)


def load_workbook(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            rows = json.load(f)
    except Exception:
        raise InvalidFileException(f"Cannot read {path}")
    return Workbook(rows)


class InvalidFileException(Exception):
    pass


def ensure_openpyxl_stub():
    module = SimpleNamespace(
        Workbook=Workbook,
        load_workbook=load_workbook,
        utils=SimpleNamespace(
            exceptions=SimpleNamespace(InvalidFileException=InvalidFileException)
        ),
    )
    sys.modules.setdefault("openpyxl", module)
