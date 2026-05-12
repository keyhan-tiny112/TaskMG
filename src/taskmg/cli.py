"""
CLI(Command line interface) of TaskMG
Use: taskmg [option] 
"""
# src/cli.py
#  ---
# TaskMG  
# Copyright 2026 Keyhan

# This product includes software developed by Keyhan 
# for the TaskMG project.

# Licensed under the Apache License, Version 2.0.
# See the LICENSE file for full details
import typer
from typer import echo, secho
from repo import TaskRepo, Task
from pathlib import Path
from typing import Literal, Tuple, Union
# from importlib.metadata import version

app = typer.Typer(
    name="pipe",
    help="taskmg is a lightweight task manager built around a simple, fast and human-readable file format called '.task'.",
    short_help="taskmg's a task manager for saving task\state\log in .task file."
)
group_app = typer.Typer(name="group")
custom_app = typer.Typer(name="custom")

app.add_typer(group_app, name="group", help="Manage a groups")
app.add_typer(custom_app, name="custom", help="Mnanage a 'custom' in the tasks")

def get_repo():
    return TaskRepo(str(Path.cwd() / "tasks.task"))


# ----------- GROUPS -----------


# --- ADD ---

@group_app.command(help="add a Group and add task in Group", name="add")
def add_group(
    name: str,
    ids: Tuple[int]
):
    repo = get_repo()

    task = repo.add_group(name, ids)

    secho("Added Group!", fg="green")
    secho(task.serialize(), fg="blue")

# --- REMOVE ---

@group_app.command(help="remove a Group", name="remove")
def remove_group(name: str):
    repo = get_repo()

    repo.remove_group(name)

    secho("removed Group!", fg="green")

# --- LIST ---

@group_app.command(help="List a Groups", name="list", no_args_is_help=True)
def lst_group():
    repo = get_repo()

    num = 0

    for group in repo.list_groups():
        num += 1
        echo(f"{num}. {group}")

# --- SHOW ---

@group_app.command(help="Show of details Group", name="show")
def show_group(name: str):
    repo =  get_repo()

    tasks = repo.get_group(name)

    for t in tasks:
        secho(f"\nTask {t.num}:", fg="yellow")
        secho(t.serialize(), fg="blue")
        
# --- ADD-IN-GROUP ---

@group_app.command(name="add-in-group", help="add task in the Group")
def add_in_group(
    group_name: str,
    name: str,
    start: str,
    end: str,
    desc: str | None= typer.Option(None, "--desc", "desc", help="add desc in task"),
    done: bool = typer.Option(False, "-done", is_flag=True, help="done of Task")
):
    repo = get_repo()

    num = repo._next_id()

    task = Task(num, name, start, end, done=done, desc=desc)

    repo.add_task_in_group(name, task)

    secho("Added task in Group!", fg="green")

# ----------- ADD --------------


@app.command(help="add a task in .task file", short_help="add a task")
def add(
    name: str,
    start: str,
    end: str,
    desc: str | None = typer.Option("--desc", help="add desc in task"),
    done: bool = typer.Option(False, "-done", is_flag=True, help="done of Task", flag_value=bool)
):
    repo = get_repo()

    task = repo.add(name, start, end, desc)

    if done:
        repo.complete(task.num)

    secho("Added Task!\nLook:", fg="green")
    secho(task.serialize(), fg="blue")


# ------------- LIST -----------


@app.command(help="show list of task in task file", short_help="show list", name="list")
def lst():
    repo = get_repo()
    tasks = repo.list_tasks()

    if not tasks:
        secho("No tasks", fg="red")
        return

    for t in tasks:
        secho(f"{t.num}:", fg="yellow")
        secho(t.serialize(), fg="blue")


# ---------- COMPLETE ---------


@app.command(help="complete task in Task file", short_help="complete task")
def done(num: int):
    repo = get_repo()

    if repo.complete(num):
        secho("completed", fg="green")
    else:
        secho("not found", fg="red")


# ---------- REMOVE ----------


@app.command(help="remove task form Task file", short_help="remove task")
def remove(num: int):
    repo = get_repo()

    if repo.remove(num):
        secho("removed", fg="green")
    else:
        secho("not found", fg="red")


# ---------- REPLACE ----------


@app.command(help="edit task in Task file", short_help="edit task")
def replace(
    num: int,
    name: str | None,
    start: str | None,
    end: str | None,
    done: bool | None,
    desc: str | None = typer.Option(None, "--desc", help="description of task"),
):
    repo = get_repo()

    if desc:
        repo.edit(num, name, start, end, done, desc=desc)
    else:
        repo.edit(num, name, start, end, done)

    echo(f"{typer.style("edit of task:", fg="yellow")}\n{typer.style(repo.get(1).serialize(), fg="blue")}")


# ----------- SHOW ------------


@app.command(help="show of your task", short_help="show task")
def show(num: int):
    repo = get_repo()
    secho(repo.get(num).serialize(),fg="blue")


# ---------- OUTPUT ------------


@app.command(help="show name/start/end of your task", short_help="show data of task")
def output(num: int, select: Literal['name', 'start', 'end']):
    repo = get_repo()

    match select.upper().strip():
        case "NAME":
            secho(repo.get(num).name, fg="yellow")
        case "START":
            secho(repo.get(num).start, fg="yellow")
        case "END":
            secho(repo.get(num).end, fg="yellow")
        case _:
            echo("ha?")


# ------------ FIND ------------


@app.command(help="find a task in task file", short_help="find a task")
def find(
    name: str | None,
    start: str | None,
    end: str | None,
    done: Literal['true', 'false']
):
    repo = get_repo()

    done_val = done == "true"

    idtask = repo.search(name=name, start=start, end=end, done=done_val)

    if idtask is None:
        secho("not found", fg="red")
    else:
        secho("found Task!\nLook:", fg="green")
        secho(repo.get(idtask).serialize(), fg="blue")


if __name__ == "__main__":
    app()
