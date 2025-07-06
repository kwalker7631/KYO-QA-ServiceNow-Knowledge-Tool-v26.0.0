import os

def test_ci_workflow_exists():
    assert os.path.isfile(os.path.join('.github', 'workflows', 'ci.yml'))
