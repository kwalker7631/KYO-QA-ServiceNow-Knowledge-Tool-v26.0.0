import processing_engine

def test_process_job_calls_helpers(monkeypatch):
    called = []
    monkeypatch.setattr(processing_engine, 'fetch_data', lambda job: called.append('fetch') or {})
    monkeypatch.setattr(processing_engine, 'parse_data', lambda data: called.append('parse') or {})
    monkeypatch.setattr(processing_engine, 'export_results', lambda parsed, job: called.append('export'))
    processing_engine.process_job({}, {})
    assert called == ['fetch', 'parse', 'export']
