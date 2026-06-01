---
title: Taskmg
author: Keyhan
date: 2026-03-20
tags: [programming, python, metadata, task manager]
---
<center>
<h2><i><strong>Table of Contents</strong></i></h2>
<details>
  For fast lookup on Parts of Document
  and fast travel in the Parts.
</details>
</center>

- [Why `Taskmg`](#taskmg)
- [Why `.task`?](#why-task)
- [Task Group](#task-groups-added-in-v13)
- [`Python` example](#python-example)
- [installation](#installation)
- [Project status](#project-status)
- [Customization](#customization)
- [Custom field](#custom-field-added-on-v16)
- [`Taskmg` http API](#task-api)
- [license](#license)
- [CONTRIBUTING](#contributing)
- [Final words](#final-words)

# Taskmg
Taskmg is a lightweight task manager built around a simple, fast and human‑readable file format called `.task`.

Instead of using databases or heavy structured formats, taskmg stores tasks as structured text blocks that can be easily read and edited with any text editor.

The goal of the project is to keep task storage:

- simple
- readable
- lightweight
- easy to modify
- and fast
# Why .task?
Many applications store tasks in *JSON* or databases.

While these formats are powerful, they are often difficult for humans to read or modify manually.

For example, a task stored in *JSON* might look like this:

```json
{
  1: {
    "name": "workout",
    "start": "12:00",
    "end": "13:00",
    "created": "2026-03-20",
    "done": false,
    "desc": "gym training"
  }
}
```
With *taskmg*, the same task can be stored like this:

```task
$$ Task Repository File
$$ version: 1.4

@task 1
name = workout
start = 12:00
end = 13:00
created = 2026-03-20
done = false
desc = gym training
```
This format is designed to be:

- easy to read
- easy to edit
- easy to parse programmatically
# Task Groups (Added in v1.3)
Starting from `v1.3`, tasks can optionally belong to a group.

Groups allow tasks to be organized by category, project, or context.

***Example***:

```task
$$ Task Repository File
$$ version: 1.4

[work]
@task 1
name = coding
start = 10:00
end = 12:00
created = 2026-03-20
done = false

@task 2
name = deploy
start = 12:30
end = 13:00
created = 2026-03-20
done = false
```
A group header is written as:

```text
[group_name]
```
All tasks that follow belong to that group.

# Python Example
Using *taskmg* in Python:

```python
from taskmg import TaskRepo

repo = TaskRepo("tasks.task")

#                 NAME   | START  | END    | DESC
task = repo.add("workout", "12:00", "12:30", "gym training")

print(task.name, task.start, task.end)
```
***Example output***:

```text
workout 12:00 12:30
```
Working With Groups
Groups can be managed directly through the repository API.

***Example***:

```python
repo = TaskRepo("tasks.task")

repo.add("coding", "10:00", "12:00")
repo.add("deploy", "09:30", "13:00")

repo.add_group("work", 1, 2)

groups = repo.list_groups()
print(groups)
```
***Output***:

```text
['work']
```
Retrieve tasks from a group:

```python
tasks = repo.get_group("work")

for t in tasks:
    print(t.name)
Editing Tasks
```
Tasks can be edited through the repository **API**.

***Example***:

```python
repo.edit(1, name="morning workout")

repo.complete(1)

repo.remove(1)
```
You can also access tasks like objects:

```python
task = repo[1]

print(task.name)

task.name = "new name"
```
# Installation
Install from source:

```bash
git clone github.com/keyhan-tiny112/TaskMG
cd <directory>
# install package
pip install -e .
```
Install from *PyPI* (Recommand):

```bash
pip install taskmg
```
# Project Status
taskmg is under active development.

The internal format and repository system evolve gradually as new features are added.

Format evolution:

```text
v1.1  basic task blocks
v1.2  description field
v1.3  task groups
v1.4  grouped storage system
```
Future releases may introduce improvements such as:

- faster parsing
- indexing
- improved tooling
# Customization
Because taskmg is *open‑source* and written in *Python*, developers can extend the format.

For example, custom fields could be added:

```task
priority = high
location = gym
```
Extending the parser allows taskmg to support additional metadata fields.
# custom field (Added on v1.6)
# License
TaskMG is licensed under the **Apache License, Version 2.0**.

You may use, modify, distribute, and integrate TaskMG in commercial or open‑source projects, provided you comply with the terms of the Apache 2.0 License.

This project includes a `LICENSE` file containing the full text of the license, and a `NOTICE` file that provides attribution and copyright information.

Copyright © 2026 Keyhan

See the **`LICENSE`** file for full details:

<p>
<a href=" LICENSE" style="padding:10px 16px; background-color:#2ea44f; color:white; text-decoration:none; border-radius:6px; font-weight:600;">
Read the LICENSE Guide
</a>
</p>

# CONTRIBUTING

If you would like to improve *taskmg*, please follow these guidelines:

- Write clear and readable *Python* code
- Public functions and classes must include docstrings
- Avoid unnecessary dependencies
- Changes to the `.task` format must be reflected in **SPEC.md**

Standard workflow:
```text
fork → branch → commit → pull request
```

See the **`CONTRIBUTING`** file for full details:

<p>
<a href=" LICENSE" style="padding:10px 16px; background-color:rgba(0, 191, 255, 0.785); color:white; text-decoration:none; border-radius:6px; font-weight:600;">
Read the CONTRIBUTING Guide
</a>
</p>

Maintainer: ***Keyhan***

# Final Words
*taskmg* started as a small experiment to explore a human‑friendly task storage format.

The project continues to evolve step by step as the repository system improves.

Ideas, improvements, and contributions are always welcome.
