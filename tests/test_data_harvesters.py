import pytest
from data_harvesters import harvest_qa_numbers, harvest_all_data


def test_harvest_qa_numbers_basic():
    text = "Issue QA-123 and SB_456 present"
    assert harvest_qa_numbers(text) == ["QA-123", "SB_456"]


def test_harvest_all_data_includes_qa_numbers():
    text = "Model KM-123 with QA-789"
    result = harvest_all_data(text, "file.pdf")
    assert result["qa_numbers"] == "QA-789"
