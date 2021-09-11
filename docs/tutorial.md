In this tutorial, you will learn, how to use `census` project to track mypy coverage.

After installing the `code_census`, you need to follow three steps.

1. Create a postgres database to track metrics.
2. Fill the database with necessary details to track the project metrics.
3. Set up UI to view results in your favorite tool.

## 1. Create a new database

### Createdb

After installing [PostgreSQL](https://www.postgresql.org/), create a new database. Here I'm using `createdb` command,
please use your preferred way to create a database.

`$createdb census`


### Verify the new database

```
$psql -h localhost -d census
psql (13.3, server 13.4)
Type "help" for help.

census=#
census=# \dt
Did not find any relations.
```

The `psql` successfully logged in the database and database is empty.


## 2. Fill the database

### Create tables

You can access `code_census` CLI interface via `census` or `code_census` command.

``` bash
$census
Usage: census [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create-db
  mypy
  project
```

`census` command help section shows three commands, let's run `create-db` to create tables.

*Note*: `create-db` does not create a new database but creates tables.

To create tables you need to pass the database credentials.

``` bash
$census create-db --db-url postgresql://:@localhost:5432/census
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> cc7054b42c18, Add initial tables
/private/tmp/venv/lib/python3.9/site-packages/sqlalchemy/sql/base.py:415: SAWarning: Can't validate argument 'max_length'; can't locate any SQLAlchemy dialect named 'max'
  util.warn(
✅ The schema for census app is created
```

Now the census database is filled with tables.

``` bash
$psql -h localhost -d census
psql (13.3, server 13.4)
Type "help" for help.
census=# \dt
            List of relations
 Schema |      Name       | Type  | Owner
--------+-----------------+-------+-------
 public | alembic_version | table | user
 public | mypyrunlineitem | table | user
 public | project         | table | user
 public | run             | table | user
(4 rows)
```
*Note*: Wherever you're using `--db-url`, the same argument can be passed as environment variable `DB_URL`.

### Create a new project

Let's see project command documentation.

``` bash
$census project --help
Usage: census project [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  all
  create
```

Now let's see `project create` command documentation.

``` bash
$census project create --help
Usage: census project create [OPTIONS] NAME

Options:
  --description TEXT
  --url TEXT
  --db-url TEXT       Pass postgres connection details like
                      postgresql://postgres:pass@db.host:5432/code_census or
                      Set DB URL as environment variable like DB_URL="postgres
                      ql://postgres:pass@db.host:5432/code_census".
                      [required]
  --help              Show this message and exit.
```

`create` command takes in mandatory `NAME`, optional `--description, --url, --db-url`.
Let's create a project for `code_census`.

``` bash
$census project create code_census --description "A CLI tool to track code metrics" --url "https://github.com/kracekumar/code_census" --db-url postgresql://:@localhost:5432/census
Project created. project=<Project(id=2, name=code_census, description=A CLI tool to track code metrics)>
```

Now the project is successfully created.

### project all command

``` bash
$census project all --db-url postgresql://:@localhost:5432/census
                                             Projects
┏━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Name        ┃ Description                      ┃ URL                                       ┃
┡━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ code_census │ A CLI tool to track code metrics │ https://github.com/kracekumar/code_census │
└────┴─────────────┴──────────────────────────────────┴───────────────────────────────────────────┘
```

`all` sub-command displays all the projects.

### Upload mypy run report

*Note*: mypy report can be generated using `--html-report` flag like `mypy --config-file=pyproject.toml . --html-report /tmp/code_census`

``` bash
$census --help
Usage: census [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create-db
  mypy
  project
```

We have used `create-db` and `mypy` command and now it's time to use mypy command.

Let's see the `mypy` sub-command documentation

``` bash
$census mypy --help
Usage: census mypy [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  run
```

`mypy` sub-command has one more sub-command `run`.

``` bash
$census mypy run --help
Usage: census mypy run [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add
  all
  get-info
```

`run` has further three sub-commands, `add, all, get-info`. Let's see the documentation for add command.

``` bash
$census mypy run add --help
Usage: census mypy run add [OPTIONS] PROJECT_NAME

Options:
  --artifact-url TEXT
  --run-info JSON
  --mypy-coverage-file PATH  [required]
  --db-url TEXT              Pass postgres connection details like postgresql:
                             //postgres:pass@db.host:5432/code_census or Set
                             DB URL as environment variable like DB_URL="postg
                             resql://postgres:pass@db.host:5432/code_census".
                             [required]
  --help                     Show this message and exit.
```

### Upload the artifact

Now that mypy coverage report is available, let's upload the coverage info.

``` bash
$census mypy run add  code_census --run-info '{"git": {"commit": "0c9b759639ed4025522370b81ade06d1efa64bed", "version": "0.0.8"}}' --mypy-coverage-file code_census/index.html --db-url postgresql://:@localhost:5432/census
Created a new run=<Run(id=1, project_name=code_census)
Added 7 file coverages
```
We passed on following information to the `add` sub-command.

- project name: `code_census`
- `--run-info` is a JSON data details of the run and project. Here `git` JSON object contains `commit` and `version`.
- `--mypy-coverage-file` path to coverage file `index.html`.
- `--db-url` database details

### View the run details in terminal

Now to view the run details, we can use `get-info` sub-command. Let's see the documentation

``` bash
$census mypy run get-info --help
Usage: census mypy run get-info [OPTIONS] RUN_ID

Options:
  --db-url TEXT  Pass postgres connection details like
                 postgresql://postgres:pass@db.host:5432/code_census or Set DB
                 URL as environment variable like
                 DB_URL="postgresql://postgres:pass@db.host:5432/code_census".
                 [required]
  --help         Show this message and exit.
```

We know the run id, it's `1`.

``` bash
$census mypy run get-info 1 --db-url postgresql://:@localhost:5432/census
               Mypy Coverage for Run ID: 1
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┓
┃ File                            ┃ Imprecision ┃ Lines ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━┩
│ cc7054b42c18_add_initial_tables │ 64.0 %      │ 75    │
│ code_census                     │ 0.0 %       │ 3     │
│ code_census.cli                 │ 38.96 %     │ 231   │
│ code_census.formatter           │ 17.07 %     │ 41    │
│ code_census.models              │ 40.98 %     │ 122   │
│ code_census.mypy_utils          │ 28.07 %     │ 57    │
│ env                             │ 35.37 %     │ 82    │
│ --                              │ --          │ --    │
│ Summary                         │ 32.06 %     │ 611   │
│ --                              │ --          │ --    │
└─────────────────────────────────┴─────────────┴───────┘
```
Now the get-info command prints all the mypy coverage in the `code_census` file.

### Display all run details for the project

``` bash
$census mypy run all code_census  --db-url postgresql://:@localhost:5432/census
                                                  All runs for project: code_census
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Created At                 ┃ Run Info                                                                            ┃ Line Items ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1  │ 2021-09-09 16:48:24.865040 │ {'git': {'commit': '0c9b759639ed4025522370b81ade06d1efa64bed', 'version': '0.0.8'}} │ 7          │
└────┴────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────┴────────────┘
```

## 3. Create dashboard

To view all the runs data and how the coverage is moving, we can use charts. There are different solutions like [Apache Superset](https://superset.apache.org/), [Metabase](https://www.metabase.com/), etc ...

### Metabase

Metabase uses [questions](https://www.metabase.com/docs/latest/users-guide/04-asking-questions.html) and [dashboards](https://www.metabase.com/docs/latest/users-guide/07-dashboards.html) to visualize and understand the data.

We will be creating a question and the add the question to the dashboard.


After logging into the metabase as an admin, go to `Settings -> Admin`.

### Step 1 - Start

From the top-bar, click on `Databases`.

![Select Database](images/metabase/0-select-databases.png)

### Step 2 - Add Database

Click `Add Database` button and add the connection details (metabase does not allow empty username and password).

![Add Database](images/metabase/1-add-database.png)

After adding the details, from settings click `exit admin`.

### Step 3 - Select Database

In the home screen, select `census` database.

![Home Page](images/metabase/2-home-page.png)

### Step 4 - Table View

After clicking the `census`, the tables are displayed.

![Tables](images/metabase/3-census-tables.png)

### Step 5 - Browse Data

Click on the table, `mypyrunlineitem`. The page shows all the rows in the table.

![Mypy Table](images/metabase/4-mypyrunlineitem.png)

### Step 6 - SQL Query

Now let's write a simple SQL query to get the `imprecision` by run.

![Ask Question](images/metabase/4.1-ask-question-options.png)

In the SQL editor, type the query, `select run_id, avg(imprecision) as imprecision from mypyrunlineitem group by run_id;`.
You will see the results with two columns `run_id, imprecision`.

![Query Result](images/metabase/5-query-result.png)

### Step 7 - Visualization

Now select the visualization tab in the lower left bar. Select the chart as `Line Chart` and X-axis as `run_id` and Y-axis as `imprecision`.

![Visualization](images/metabase/6-visulalization.png)

### Step 8 - Question

Now Click on the `save` button on the right corner. Enter the details as show in the image and save the question.

![Save Question](images/metabase/7-save-question.png)

### Step 9 - Add to dashboard

Click `Yes please!` in the next dialog box for the question, `Saved! Add this to dashboard?`.

![Add Dashboard](images/metabase/8-add-to-dashboard.png)

### Step 10 - New Dashboard

Enter the new dashboard details as show in the image.

![Coverage Dashboard](images/metabase/9-mypy-coverage-dashboard.png)

### Step 11 - Save Dashboard

Click on the `Save` button on the right corner to save the dashboard.

![Dashboard Save](images/metabase/10-dashboard-save.png)

### Step 12 - Dashboard

Finally dashboard contains one question.

Now you can create more questions and add to the dashboard and have a view of your project!

![Dashboard View](images/metabase/11-dashboard-view.png)


*Note*: All the screenshots are taken from the metabase Mac App, the interface and menus may look different.
