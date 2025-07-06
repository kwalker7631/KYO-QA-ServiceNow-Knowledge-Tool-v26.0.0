from pathlib import Path


def test_apply_patches_script_exists():
    script = Path('apply_patches.sh')
    assert script.exists(), 'apply_patches.sh should exist'
    content = script.read_text()
    assert 'git status' in content
    assert 'pytest --maxfail=1' in content
