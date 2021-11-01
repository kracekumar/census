from code_census.mypy_utils import get_type_coverage, FileSummary

def test_get_type_coverage():
    summaries = get_type_coverage("tests/files/index.html")

    assert len(summaries) > 0

    for summary in summaries:
        assert isinstance(summary, FileSummary)
