"""Mypy coverage html file utils
"""
from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup  # type: ignore
import re


@dataclass
class FileSummary:
    full_filename: str
    imprecision: float
    lines: int


class ClassName:
    FILENAME = "summary-filename"
    IMPRECISION = "summary-precision"
    LINES = "summary-lines"


INT_REGEX = "[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"


def get_type_coverage(cov_filename: Path) -> list[FileSummary]:
    with open(cov_filename) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    run_summary: RunSummary = None  # type: ignore
    file_summaries: list[FileSummary] = []

    for tr in soup.table.find_all("tr"):
        # Get all the file summaries
        full_filename, imprecision, lines, top_level_module = "", 0.00, 0, ""
        for td in tr.find_all("td"):
            val = td.get_text()
            classes = td.get("class")
            if ClassName.FILENAME in classes:
                full_filename = val

            elif ClassName.IMPRECISION in classes:
                vals = re.findall(INT_REGEX, val)
                if vals:
                    imprecision = float(vals[0])

            elif ClassName.LINES in classes:
                vals = re.findall(INT_REGEX, val)
                if vals:
                    lines = vals[0]

        if full_filename:
            file_summaries.append(
                FileSummary(
                    full_filename=full_filename, imprecision=imprecision, lines=lines
                )
            )
    return file_summaries
