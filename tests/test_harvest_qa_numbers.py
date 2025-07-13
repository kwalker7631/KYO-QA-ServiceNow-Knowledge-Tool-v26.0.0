from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import data_harvesters as dh


def test_harvest_qa_numbers_simple():
    text = "Model TASKalfa 300i referenced QA123 and SB-456"
    qa = dh.harvest_qa_numbers(text)
    assert "QA123" in qa and "SB-456" in qa
    data = dh.harvest_all_data(text, "sample.pdf")
    assert "QA123" in data.get("qa_numbers", "")
