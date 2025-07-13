import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data_harvesters import harvest_all_data, harvest_qa_numbers


def test_harvest_qa_numbers_only():
    text = "QA-1001 and SB_2002 are references"
    numbers = harvest_qa_numbers(text)
    assert set(numbers) == {"QA-1001", "SB_2002"}


def test_harvest_all_data_includes_qa_numbers():
    text = "TASKalfa 4002i QA-3003 SB-4004"
    data = harvest_all_data(text, "sample.txt")
    assert "QA-3003" in data["qa_numbers"]
    assert "SB-4004" in data["qa_numbers"]

