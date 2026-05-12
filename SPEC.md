TaskRepo v1.4.5 – Full Technical Specification
🔢 Version Metadata
Field	Value
Version	1.4.5
Format Version Header in File	$$ version: 1.4
Language	Python 3.10+
Dependencies	Standard library only (pathlib, datetime, dataclasses, typing)
Status	Stable (Pre‑v1.5)
Maintainers	keyhan and contributors
Files Affected	.task (main data), taskrepo.py (code), SPEC.md, README.md
🌐 Overview
Purpose
TaskRepo is a minimal file‑based task management engine allowing users to store, edit, group, and query tasks stored in plain .task files.

Each .task file acts as a repository containing one or more task blocks with optional grouping sections.

Key Characteristics
Human‑readable format (.task text file).
Fully offline; no DB or external dependency needed.
Deterministic and grouped file layout (_write_grouped).
Supports CRUD operations, grouping, and inline editing via proxy.
Stable serialization compatible with all 1.4.x versions.
🧱 .task File Format – v1.4 Specification
Each .task file consists of:

A mandatory header
One or more task blocks, optionally organized by groups.
File Header
text
$$ Task Repository File
$$ version: 1.4
(blank line follows)

Task Block Structure
Each task is stored in a consistent text format:

```text
[<group-name>]        $$ optional
@task <id>
name = <string>
start = <HH:MM>
end = <HH:MM>
created = <YYYY-MM-DD>
done = <true|false>
desc = <string>       $$ optional
```
### Field Semantics
Field | Type | Description
:---- | :---: | :--------
@task <id>	Integer	Unique task identifier
name	String	Display name of the task
start	HH:MM	Task starting time (validated)
end	HH:MM	Task ending time, must be after start
created	Date (YYYY-MM-DD)	Automatically generated creation date
done	Boolean (true/false)	Task completion state
desc	String (optional)	User description
[group]	String (optional)	Logical category prefix
# 🧩 Data Classes
Task (core dataclass)
```python
@dataclass
class Task:
	num: int
	name: str
	start: str
	end: str
	created_date: str
	done: bool = False
	desc: Optional[str] = None
	group: Optional[str] = None
```
### Methods
Method | Description
:----- | :-----------:
parse(block: str) -> Task	| Parses a text block into a Task object. Handles optional [group] prefix.
serialize() -> str | Converts the object back into .task text format. Includes group header and desc if available.

> * Parsing and serialization are symmetric and deterministic.
# 🗂️ TaskRepo Class
Central engine managing CRUD operations and grouped write architecture.

### Header
```python
HEADER = "$$ Task Repository File\n$$ version: 1.4\n\n"
```
### Constructor
```python
repo = TaskRepo(path="tasks.task")
```
Automatically:

- normalizes to absolute path
- creates the file with header if missing
- ensures file extension is `.task`
# ⚙️ Internal Architecture (v1.4.5)
## Key Private Methods
Method | Description
:----- | :-------------:
`_read_blocks()` | Reads and splits file content into raw task blocks, ignoring header lines starting with `$$`.
`_write_grouped(tasks: list[Task])`	| Writes all tasks back grouped by their group attribute. Groups appear in sorted order; ungrouped tasks come first.
`_next_id()` | Returns the next incremented ID.
`_write_block(...)`	| Removed in v1.4.5 — replaced entirely by _write_grouped.
`_write_grouped()` | Behavior in Detail
</br>

```text
Ungrouped tasks
↓
Groups in sorted order
  ↓
    Each group header “[name]”
    Each task block body without redundant group headers
```
Example Output:

```task
$$ Task Repository File
$$ version: 1.4

@task 1
name = coding
start = 09:00
end = 10:00
created = 2026-03-31
done = false
desc = write code

[work]
@task 2
name = meeting
start = 11:00
end = 12:00
created = 2026-03-31
done = false
```
# ✨ Public APIs
## CRUD Operations
Method | Description | Notes
:----- | :---------- | :--------:
add(name, start, end, desc=None) | Adds new task. Auto assigns ID and creation date. | Time validated as HH:MM
edit(num, **fields)	| Updates fields by ID.	| Uses _write_grouped()
remove(num)	| Deletes the task by ID.	| Bug fixed in 1.4.5 (writes new_tasks instead of all).
complete(num)	| Marks task as done.	
exists(num)	| Checks if a task exists.	
list_tasks() | Returns all parsed tasks.	
get(num) | Returns Task object by ID or dummy Task if not found.
`return_task(num, output=False	True	“ret_block”)`
## Group Management
Method | Purpose
 :----- | :----------:
add_group(name, *ids)	| Assigns existing tasks to a named group.
remove_group(name) | Removes group labels from all tasks in that group.
get_group(name) -> list[Task]	| Lists all tasks in the given group.
edit_in_group(name, target, value)	Bulk edits all tasks in a group (e.g., mark all done).
add_task_in_group(name, task)	Adds new task and associates it with group.
list_groups()	Lists all existing group names sorted.
## Helper / Misc Functions
Method | Description
 :------ | :----------------:
clear() | Clears file content and resets header.
search(**kwargs) | Returns first task ID matching given field filters. Used for quick lookup.
add_sample() | Adds three sample tasks (demo method).
## Proxy System (_TaskProxy)
Lightweight interface that allows direct field mutation of tasks while automatically updating the file.

```python
repo = TaskRepo("tasks.task")
t = repo[1]
t.name = "new name"   # triggers repo.edit()
del t.desc             # triggers repo.edit(num, desc=None)
```
This enables intuitive object-like mutation of tasks.
# 🧠 Fixed Bugs and Changes Since v1.4
Area | Description
 :-------- | :---------------:
Writing System | Removed _write_block; all writes now through _write_grouped() for proper grouping.
Deterministic Ordering | _write_grouped() sorts groups alphabetically to ensure reproducible output.
edit_in_group | Fixed logic bug (t.name = name → t.name = value).
remove() | Corrected to write only new_tasks (previously rewrote all tasks).
add()	| Avoided redundant recalculation of num and date.
Group | sorting	Ensures file consistency and clear group separation.
Placeholders added | Introduced self._cache and self._index for future performance optimization (v1.5).
# 📦 Internal State Placeholders (for migration to v1.5)
Property | Purpose
 :------- | :-------:
_cache: Optional[list[Task]] | Memory cache for loaded tasks to skip repeated parsing.
_index: dict[int, int] | Offset index reserved for .task.index file.

> * (Not active in 1.4.5, just initialized.)
## 🔍 TaskRepo File Example (v1.4.5)
```task
$$ Task Repository File
$$ version: 1.4

@task 1
name = write documentation
start = 10:00
end = 11:30
created = 2026-03-31
done = true
desc = finishing SPEC

[work]
@task 2
name = review code
start = 14:00
end = 15:30
created = 2026-03-31
done = false

@task 3
name = meeting
start = 16:00
end = 17:00
created = 2026-03-31
done = false
desc = prepare notes
```
## 💡 Execution Example
```python
from taskmg import TaskRepo

repo = TaskRepo("tasks.task")

# Add tasks
repo.add("Design phase", "09:00", "10:00")
repo.add("Write Tests", "10:15", "12:00", desc="Unit tests for modules")

# Grouping
repo.add_group("work", 1, 2)

# Retrieve and modify
task = repo[1]
task.done = True    # auto-updates repo
```
# ⚙️ Version Compatibility
Feature	Introduced | Notes
 :--------------- | :---------:
desc field	v1.2 | Optional text field
group field	v1.3 | Group tagging supported
Grouped Write Engine (_write_grouped)	v1.4 | Fixed in 1.4.5
Cache + Index placeholders v1.4.5	| Activated in v1.5
## 🧮 Complexity Summary
Operation	Complexity | Comments
 :------------------| :----------:
add, edit, remove	O(N) | Rewrites file grouped
search, get, exists	O(N) | Reads all tasks each time (no indexing yet)
add_group, remove_group, edit_in_group	O(N) | Group traversal
list_groups	O(N) | Extracts set of t.group values

## 🧭 Roadmap to v1.5
Area	| Planned Enhancement
:------ | :--------------------:
Indexing | `.task.index` file for id -> file_offset mapping
Caching	| Persistent in-memory cache to avoid re-parsing
Filter API | Replace search() with advanced filter(**conditions)
Group Proxy API |	repo.group("work").complete_all()
Sorting / Range | Queries	Order by time, date, or name
Export / Import	JSON & CSV | structured export
CLI Wrapper	| Introduce command-line layer taskmg
TaskQL Mini-DSL |	Optional query language once engine stabilizes
</br>
# ✅ Summary Statement
Version `v1.4.5` of TaskRepo represents a stabilized, production‑ready stage of the .task engine:

- deterministic grouped file architecture
- functional, symmetrical parsing and serialization
- correct CRUD semantics
- consistent internal API design
- prepared for future caching/indexing