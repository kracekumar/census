from .models import Project, MypyRunLineItem
from rich.table import Table


def format_projects(projects: list[Project]) -> Table:
    table = Table(title=f"Projects")
    if projects:
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("URL")

        for project in projects:
            table.add_row(
                f"{project.id}",
                f"{project.name}",
                f"{project.description}",
                f"{project.url}",
            )
    else:
        table.add_column("No Projects")

    return table


def format_mypy_items(run_id: int, items: list[MypyRunLineItem]) -> Table:
    table = Table(title=f"Mypy Coverage for Run ID: {run_id}")
    table.add_column("File")
    table.add_column("Imprecision")
    table.add_column("Lines")

    total_imprecision, total_loc = 0, 0
    for item in items:
        table.add_row(item.path, f"{item.imprecision} %", f"{item.loc}")
        total_imprecision += item.imprecision
        total_loc += item.loc
    avg = total_imprecision / len(items)
    table.add_row("--", "--", "--")
    table.add_row("Summary", f"{avg:.2f} %", f"{total_loc}")
    table.add_row("--", "--", "--")
    return table
