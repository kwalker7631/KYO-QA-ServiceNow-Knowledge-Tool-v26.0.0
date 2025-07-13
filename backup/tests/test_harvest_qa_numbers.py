from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import data_harvesters as dh


def test_harvest_qa_numbers_simple():
    text = "Model TASKalfa 300i referenced QA123 and SB-456"
    qa = dh.harvest_qa_numbers(text)
    assert "QA123" in qa and "SB-456" in qa
    data = dh.harvest_all_data(text, "sample.pdf")
    expected_qa_numbers = ["QA123", "SB-456"]
    actual_qa_numbers = data.get("qa_numbers", "").split(", ")
    assert actual_qa_numbers == expected_qa_numbers
