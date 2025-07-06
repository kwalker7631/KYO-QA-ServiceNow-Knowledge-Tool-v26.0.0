from pathlib import Path

def test_verify_revert_script_exists():
    script = Path('verify_revert.sh')
    assert script.exists(), 'verify_revert.sh should exist'
    content = script.read_text()
    assert 'git status --porcelain' in content
    assert 'pytest --maxfail=1 --disable-warnings -q' in content
