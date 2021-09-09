"""CLI
"""
import click
from pathlib import Path
import os
import sys
from code_census.models import (
    Project,
    Run,
    MypyRunLineItem,
    create_session,
    create_engine,
    get_project,
    add_run,
    add_mypy_line_items,
    get_mypy_line_items_by_run_id,
    get_runs,
    get_projects,
)
from code_census.mypy_utils import get_type_coverage
from code_census import formatter
from alembic.config import Config
from alembic import command
from rich.console import Console
from rich.table import Table


HELP_TEXT = {
    "db_url": 'Set DB URL as environment variable like DB_URL="postgres://postgres:pass@db.host:5432/somedb".'
}

error_console = Console(stderr=True, style="bold red")
info_console = Console(style="black green")


class JSONType(click.ParamType):
    name = "json"

    def convert(self, value, param, ctx):
        import json

        if isinstance(value, (dict, list)):
            return value
        try:
            converted_value = json.loads(value)
        except json.decoder.JSONDecodeError:
            self.fail(f"{value=} is not a valid JSON"), param, ctx

    def __repr__(self) -> str:
        return "JSON"


@click.group()
def cli():
    pass


@cli.group()
def mypy():
    pass


@mypy.group()
def project():
    pass


@project.command()
@click.argument("name", type=str, required=True)
@click.option("--description", type=str, default="")
@click.option("--url", type=str, default="")
@click.option(
    "--db-url", type=str, required=True, envvar="DB_URL", help=HELP_TEXT["db_url"]
)
def create(name: str, description: str, url: str, db_url: str):
    name = name.strip()
    session = create_session(db_url, echo=False)
    project = get_project(session, name=name)

    if project:
        error_console.print(f"Project {project.name} already exists")
        sys.exit(-1)

    project = Project(name=name, description=description, url=url)
    session.add(project)
    session.commit()
    info_console.print(f"Project created. {project=}")


@project.command()
@click.option(
    "--db-url", type=str, required=True, envvar="DB_URL", help=HELP_TEXT["db_url"]
)
def all(db_url):
    session = create_session(db_url, echo=False)
    projects = get_projects(session)
    table = formatter.format_projects(projects)
    info_console.print(table)


@mypy.group()
def run():
    pass


@run.command()
@click.argument("project_name", type=str, required=True)
@click.option("--artifact-url", type=str, required=False, default="")
@click.option("--run-info", type=JSONType(), default={})
@click.option("--mypy-coverage-file", type=click.Path(), required=True)
@click.option(
    "--db-url", type=str, required=True, envvar="DB_URL", help=HELP_TEXT["db_url"]
)
def add(
    project_name: str,
    artifact_url: str,
    run_info: dict,
    mypy_coverage_file: click.Path,
    db_url: str,
    log=True,
):
    name = project_name.strip()
    session = create_session(db_url, echo=log)
    project = get_project(session=session, name=project_name)

    if not project:
        error_console.print(f"{project_name=} is missing.")
        info_console.print("Create one using, [bold] project create name [/bold]")
        sys.exit(-1)

    run = add_run(
        session=session, project=project, artifact_url=artifact_url, run_info=run_info
    )

    cov_filename = Path(mypy_coverage_file)
    if cov_filename.exists():
        summaries = get_type_coverage(cov_filename=mypy_coverage_file)
        res = add_mypy_line_items(
            session=session, project=project, run=run, file_summaries=summaries
        )
        session.commit()
        count = len(res)
        info_console.print(f"Created a new {run=}")
        info_console.print(f"Added {count} file coverages")

    else:
        error_console.print(f"{mypy_coverage_file=} is missing")
        sys.exit(-1)


@run.command()
@click.option(
    "--db-url", type=str, required=True, envvar="DB_URL", help=HELP_TEXT["db_url"]
)
@click.argument("run_id", type=int)
def get_info(db_url: str, run_id: int):
    session = create_session(db_url, echo=False)
    items = get_mypy_line_items_by_run_id(session=session, run_id=run_id)

    if not items:
        error_console.print(f"[i] No run found for {run_id=} [/i]")
        sys.exit(-1)

    table = formatter.format_mypy_items(run_id, items)
    info_console.print(table)


@run.command()
@click.option(
    "--db-url", type=str, required=True, envvar="DB_URL", help=HELP_TEXT["db_url"]
)
@click.argument("project_name", type=str)
def all(db_url: str, project_name: str):
    session = create_session(db_url, echo=False)
    project_name = project_name.strip()
    project = get_project(session, name=project_name)

    if not project:
        # Print list of available project names
        error_console.print("{project_name=} is missing")
        sys.exit(-1)
    runs = get_runs(session=session, project=project)

    table = Table(title=f"All runs for project: {project.name}")
    table.add_column("ID")
    table.add_column("Created At")
    table.add_column("Run Info")
    table.add_column("Line Items")

    for run in runs:
        # N+1 query but it's fine for now
        count = len(run.mypylineitems)
        table.add_row(f"{run.id}", f"{run.created}", f"{run.run_info}", f"{count}")
    info_console.print(table)


@click.option(
    "--db-url", type=str, required=True, envvar="DB_URL", help=HELP_TEXT["db_url"]
)
def create_db(db_url: str):
    engine = create_engine(db_url, echo=True)
    cfg = Config("alembic.ini")
    with engine.begin() as connection:
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head", sql=True)


if __name__ == "__main__":
    cli()
