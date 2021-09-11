from sqlalchemy_utils import URLType, Timestamp
import sqlalchemy as sa
from sqlalchemy import create_engine
from typing import Optional
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from .mypy_utils import FileSummary

RUN_INFO_DESCRIPTION = """Store run details as a dictionary.

Example
-------
{
  "git": {"branch": "main", "commit_id": "8eea08c125b26aed539166207bda2f7ca1982493",
          "pr": 1},
  "execution_time": {"duration": 500, "unit": "sec"},
  "mypy": {"version": 0.912}
}
"""

Base = declarative_base()


class IDMixin(object):
    """Base class for all the models"""

    id = sa.Column(sa.BigInteger, primary_key=True)


class Project(Base, Timestamp, IDMixin):
    __tablename__ = "project"

    name = sa.Column(sa.String, unique=True, index=True)
    description = sa.Column(sa.String, nullable=True, default="")
    url = sa.Column(URLType, default="")

    def __repr__(self) -> str:
        return (
            f"<Project(id={self.id}, name={self.name}, description={self.description})>"
        )


class Run(Base, Timestamp, IDMixin):
    __tablename__ = "run"

    project_id = sa.Column(sa.Integer, sa.ForeignKey(Project.id))
    artifact_url = sa.Column(URLType, nullable=False, default="")
    run_info = sa.Column(sa.JSON)

    project = relationship(Project)
    mypylineitems = relationship("MypyRunLineItem")

    def __repr__(self) -> str:
        return f"<Run(id={self.id}, project_name={self.project.name})"


class MypyRunLineItem(Base, Timestamp, IDMixin):
    __tablename__ = "mypyrunlineitem"

    project_id = sa.Column(sa.Integer, sa.ForeignKey(Project.id))
    run_id = sa.Column(sa.Integer, sa.ForeignKey(Run.id))
    # "Path(foo/bar/custom.py) or file path representation(foo.bar.custom)"
    path = sa.Column(sa.Unicode)
    loc = sa.Column(sa.Integer)
    imprecision = sa.Column(sa.Float)

    project = relationship(Project)
    run = relationship(Run)

    def __repr__(self) -> str:
        return f"<MyprRunLineItem(path={self.path}, loc={self.loc}, imprecision={self.imprecision})"


def create_session(db_url: str, echo: bool = True):
    engine = create_engine(db_url, echo=echo)
    Session = sessionmaker(bind=engine)
    return Session()


def get_project(session, name: str) -> Optional[Project]:
    return session.query(Project).filter_by(name=name.strip()).first()


def get_projects(session) -> list[Project]:
    return session.query(Project).all()


def get_runs(session, project: Project) -> list[Run]:
    return session.query(Run).filter_by(project=project).order_by(Run.id.desc()).all()


def add_run(session, project: Project, artifact_url: str, run_info: dict) -> Run:
    run = Run(project=project, artifact_url=artifact_url, run_info=run_info)
    session.add(run)
    return run


def add_mypy_line_item(
    session, project: Project, run: Run, file_summary: FileSummary
) -> MypyRunLineItem:
    item = MypyRunLineItem(
        project=project,
        run=run,
        path=file_summary.full_filename,
        loc=file_summary.lines,
        imprecision=file_summary.imprecision,
    )
    session.add(item)
    return item


def add_mypy_line_items(
    session, project: Project, run: Run, file_summaries: list[FileSummary]
) -> list[MypyRunLineItem]:
    summaries = []
    for summary in file_summaries:
        item = add_mypy_line_item(
            session=session, project=project, run=run, file_summary=summary
        )
        summaries.append(item)
    return summaries


def get_mypy_line_items_by_run_id(session, run_id: int) -> list[MypyRunLineItem]:
    return session.query(MypyRunLineItem).filter_by(run_id=run_id).all()
