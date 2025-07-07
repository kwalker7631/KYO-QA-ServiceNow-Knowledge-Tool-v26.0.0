import re
from pathlib import Path


def test_single_cache_dir_import():
    content = Path("kyo_qa_tool_app.py").read_text()
    assert (
        len(re.findall(r"^from config import CACHE_DIR$", content, re.MULTILINE)) == 1
    )
