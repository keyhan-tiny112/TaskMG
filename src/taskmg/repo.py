# src/repo.py
# ---
# TaskMG  
# Copyright 2026 Keyhan

# This product includes software developed by Keyhan 
# for the TaskMG project.

# Licensed under the Apache License, Version 2.0.
# See the LICENSE file for full details
from pathlib import Path
from datetime import datetime, time
from typing import Union, Optional, Literal
from dataclasses import dataclass
from importlib.metadata import version
from annotated_doc import Doc
from annotated_types import Annotated
import os, struct, json

class TaskError(Exception):
    """Base error for taskmg."""
    pass

class TaskValueError(TaskError):
    """Invalid value in task."""
    pass

class TaskParseError(TaskError):
    """Error while parsing .task file."""
    pass

class TaskTimeError(TaskError):
    """Invalid time format."""
    pass

class TaskMissingFieldError(TaskError):
    """Required field is missing."""
    pass

class Task:
    """
    Represents a single task stored inside a `.task` repository file.

    Task File Specification (`v1.5`)

    ----------------------------------------
    Each task is stored as a block:

        [<name-group>] $$ Optional
        @task <id>
        name = <string>
        start = <HH:MM>
        end = <HH:MM>
        created = <YYYY-MM-DD>
        done = <true|false(bool)>
        desc = <string|none>  $$ Optional
        custom.<key> = <value> $$ Optional

    `desc` is optional and has no effect on logic.
    * desc Added on `v1.2`
    * Group Added on `v1.3`
    Note:
        comment is `$$`
    """
    def __init__(
        self,
        num: int,
        name: str,
        start: Annotated[Union[str, time], Doc("fromat: HH:MM. e.g. 09:05 or 23:20")],
        end: Annotated[Union[str, time], Doc("fromat: HH:MM. e.g. 09:05 or 23:20")],
        created_date: Annotated[Union[str, time], Doc("format: YYYY-MM-DD. e.g. 2026-10-21")] = datetime.now().strftime("%y-%m-%d"),
        done: bool = False,
        desc: Optional[str] = None,
        custom: Optional[dict[str, Union[str, list, int, float, dict]]] | None = None,
        group: Optional[str] = None
    ):
        if None in {num, name, start, end, created_date, done}:
            raise TaskMissingFieldError("num, name, start, end, created_date and done is Required param.")

        self.num = num
        self.name = name
        self.desc = desc
        self.custom = custom or {}
        self.group = group
        self.done = done

        # normalize start
        if isinstance(start, time):
            self.start = start.strftime("%H:%M")
        elif isinstance(start, str):
            self.start = datetime.strptime(start, "%H:%M").strftime("%H:%M")
        else:
            raise TaskTimeError("'start' format is HH:MM. not ", start)

        # normalize end
        if isinstance(end, time):
            self.end = end.strftime("%H:%M")
        elif isinstance(end, str):
            self.end = datetime.strptime(end, "%H:%M").strftime("%H:%M")
        else:
            raise TaskTimeError("'end' format is HH:MM. not ", end)

        if end <= start:
            start_t, end_t = self.end, self.start
            self.end = end_t
            self.start = start_t
        else:
            self.start = start
            self.end = end

        # --- normalize date ---
        
        if isinstance(created_date, time):
            self.created = created_date.strftime("%y-%m-%d")
        elif isinstance(created_date, str):
            self.created = datetime.now().strftime("%y-%m-%d")
        else:
            raise TaskTimeError("'created_date' format is YYYY-MM-DD. not ", created_date)
        
    def __repr__(self):
        repr_var = f"Task(num={self.num}, name='{self.name}', end='{self.end}' start='{self.start}' created_date='{self.created}' done={self.done}"
        
        if self.group:
            repr_var += f"group='{self.group}')"
        else:
            repr_var += ")"
        
        return repr_var

    @staticmethod
    def _normalize_time(self) -> None:
        b_start = self.start
        b_end = self.end
        # normalize start
        if isinstance(b_start, time):
            self.start = b_start.strftime("%H:%M")
        elif isinstance(b_start, str):
            self.start = datetime.strptime(b_start, "%H:%M")
        else:
            raise TaskTimeError("start format is HH:MM. not", start) from e

        # normalize end
        if isinstance(b_end, time):
            self.end = b_end.strftime("%H:%M")
        elif isinstance(b_end, str):
            self.end = datetime.strptime(b_end, "%H:%M")
        else:
            raise TaskTimeError("end format is HH:MM. not", end) from e

        if end <= start:
            start_t, end_t = self.end, self.start

        self.end = end_t
        self.start = start_t

    @staticmethod
    def parse(block: str) -> Task:
        if not isinstance(block, str):
            raise TaskParseError("invalid block for parse", block)

        try:
            lines = [l.strip() for l in block.splitlines() if l.strip()]

            group = None
            idx = 0

            # اگر اولین خط با [ شروع شود یعنی group است
            if lines[0].startswith("[") and lines[0].endswith("]"):
                group = lines[0][1:-1]
                idx = 1

            num = int(lines[idx].split()[1])
            data = {}
            custom = {}

            for line in lines[idx+1:]:
                if line.startswith("custom."):
                    k, v = line.split("=", 1)
                    key = k.split(".", 1)[1].strip()
                    try:
                        value = json.dumps(v)
                    except Exception:
                        value = v.strip()

                    custom[key] = value
                    continue

                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip()
                
        except Exception as e:
            raise TaskParseError(f"Error while Parsing. error is '{e}'") from e

        # if data.get("name") or data.get("start") or data.get("end") or data.get("created_date"): ...

        return Task(
            num=num,
            name=data.get("name"),
            start=data.get("start"),
            end=data.get("end"),
            created_date=data.get("created"),
            done=data.get("done", "").lower() == "true",
            desc=data.get("desc"),
            custom=custom,
            group=group,  # 🆕 group پارس‌شده
        )

    def serialize(self) -> str:
        """
        Convert the task to `.task` block format.
        Include `desc` only if it's given.
        """
        base = (
        f"@task {self.num}\n"
        f"name = {self.name}\n"
        f"start = {self.start}\n"
        f"end = {self.end}\n"
        f"created = {self.created}\n"
        f"done = {str(self.done).lower()}\n"
        )

        if self.desc is not None:
            base += f"desc = {self.desc}\n"

        # custom metadata
        if self.custom:
            for k, v in self.custom.items():
                base += f"custom.{k} = {v}\n"

        # 🆕 اضافه کردن group در بالا
        if self.group:
            return f"[{self.group}]\n" + base
        
        return base



class TaskRepo:
    """
    Repository manager for `.task` files (format `v1.5`)
    """

    HEADER = "$$ Task Repository File\n$$ version: 1.5\n\n"

    # --- BISK constants / structs ---

    BISK_MAGIC = b"BISK"
    BISK_VERSION = 1

    # Header struct:
    # magic(4s) version(H) flags(H)
    # task_count(Q) idx_off(Q) idx_size(Q)
    # pay_off(Q) pay_size(Q)
    # task_size(Q) task_mtime(Q)
    _BISK_HEADER_STRUCT = struct.Struct("<4sHHQQQQQQQ")

    # Index entry: task_id(Q), offset(Q), length(I)
    _BISK_ENTRY_STRUCT = struct.Struct("<QQI")

    # --- magic methods ---

    def __init__(self, path: str | Path = "tasks.task"):
        self.path: Annotated[Path, Doc("Path of .task(main) file")] = Path(path)

        if not self.path.is_absolute():
            self.path = (Path.cwd() / self.path).resolve()

        if self.path.is_dir():
            self.path = self.path / "tasks.task"

        self.index_path = self.path.with_suffix(".task.index")
        self.bisk_path = self.path.with_suffix(".bisk")

        self._index: dict[int, int] = {}
        self._cache: list[Task] | None = None
        self._bisk_index: dict[int, tuple[int, int]] | None = None

        if not self.path.exists():
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(self.HEADER)

        # ابتدا ایندکس متنی
        self._load_index()

        # سپس اگر فایل task هست، سعی کن BISK را اعتبارسنجی یا بسازی
        if self.path.exists():
            if not self._bisk_is_valid():
                try:
                    self._bisk_build()
                except Exception:
                    # اگر شکست خورد، فقط BISK را نادیده می‌گیریم
                    self._bisk_index = None

    def __getitem__(self, num: int):
        task = self.get(num)
        if task is None:
            raise TaskError(f"Task {num} not found")
        return _TaskProxy(self, task)

    def __len__(self):
        return len(self.list_tasks())

    def __contains__(self, num: int):
        return self.exists(num)

    def __iter__(self):
        return iter(self.list_tasks())

    def __setitem__(self, num: int, task: Task):
        self.edit(
            num=num,
            name=task.name,
            start=task.start,
            end=task.end,
            created=task.created,
            complete=task.done,
            desc=task.desc,
        )

    def __repr__(self):
        return f"TaskRepo(path='{self.path}', tasks={len(self)})"

    def __delitem__(self, num: int):
        self.remove(num)

    def __str__(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return file.read()

    # ============================= methods =============================

    @property
    def credit(self):
        print("keyhan and other.")

    @property
    def HELP(self):
        print(
            "go type this:\n",
            """
            from taskmg import Taskinfo

            Taskinfo.get_started()

            or:
            
            example = Taskinfo.example()
            example.example_add()
            and...
            """,
        )

    # --- dev methods ---

    def _load_index(self) -> dict[int, int]:
        idx: dict[int, int] = {}

        if not self.index_path.exists():
            self._index = {}
            return idx

        with open(self.index_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                i, off = line.split(":")
                idx[int(i)] = int(off)

        self._index = idx
        return idx

    # ============================= BISK helpers =============================

    def _task_file_stats(self) -> tuple[int, int]:
        """
        :return: (size, mtime_epoch)
        """
        st = self.path.stat()
        size = st.st_size
        mtime = int(st.st_mtime)
        return size, mtime

    def _bisk_is_valid(self) -> bool:
        """
        Check if .bisk file exists and matches current .task file.
        """
        if not self.bisk_path.exists():
            return False

        try:
            with self.bisk_path.open("rb") as f:
                header_data = f.read(self._BISK_HEADER_STRUCT.size)
                if len(header_data) != self._BISK_HEADER_STRUCT.size:
                    return False

                (
                    magic,
                    version,
                    flags,
                    task_count,
                    idx_off,
                    idx_size,
                    pay_off,
                    pay_size,
                    task_size,
                    task_mtime,
                ) = self._BISK_HEADER_STRUCT.unpack(header_data)

                if magic != self.BISK_MAGIC:
                    return False

                if version != self.BISK_VERSION:
                    return False

                cur_size, cur_mtime = self._task_file_stats()
                if task_size != cur_size or task_mtime != cur_mtime:
                    return False

                return True
        except OSError:
            return False

    def _bisk_build(self) -> None:
        """
        (Re)build .bisk from the current `.task` file.

        Linear scan over the text file to find each `@task` block
        and compute its byte offset and byte length.
        """
        if not self.path.exists():
            return

        data = self.path.read_bytes()
        size, mtime = self._task_file_stats()

        entries: list[tuple[int, int, int]] = []  # (task_id, offset, length)

        offset = 0
        current_offset: Optional[int] = None
        current_id: Optional[int] = None

        lines = data.splitlines(keepends=True)

        for line in lines:
            decoded = line.decode("utf-8", errors="replace")
            stripped = decoded.strip()

            # skip header comments
            if stripped.startswith("$$") and current_id is None and current_offset is None:
                offset += len(line)
                continue

            # group line: شروع بلاک جدید
            if stripped.startswith("[") and stripped.endswith("]"):
                if current_id is not None and current_offset is not None:
                    length = offset - current_offset
                    entries.append((current_id, current_offset, length))
                    current_id = None
                    current_offset = None

                current_offset = offset

            elif stripped.startswith("@task"):
                # پایان بلاک قبلی بدون group
                if current_id is not None and current_offset is not None:
                    length = offset - current_offset
                    entries.append((current_id, current_offset, length))

                # parse id
                parts = stripped.split()
                tid: Optional[int] = None
                if len(parts) >= 2:
                    try:
                        tid = int(parts[1])
                    except ValueError:
                        tid = None

                current_id = tid
                if current_offset is None:
                    current_offset = offset

            offset += len(line)

        # آخرین بلاک
        if current_id is not None and current_offset is not None:
            length = len(data) - current_offset
            entries.append((current_id, current_offset, length))

        # نوشتن هدر و جدول
        tmp_path = self.bisk_path.with_suffix(".bisk.tmp")

        with tmp_path.open("wb") as f:
            task_count = len(entries)
            idx_off = self._BISK_HEADER_STRUCT.size
            idx_size = task_count * self._BISK_ENTRY_STRUCT.size

            pay_off = 0
            pay_size = 0

            header = self._BISK_HEADER_STRUCT.pack(
                self.BISK_MAGIC,
                self.BISK_VERSION,
                0,  # flags
                task_count,
                idx_off,
                idx_size,
                pay_off,
                pay_size,
                size,
                mtime,
            )
            f.write(header)

            for tid, off, length in entries:
                if tid is None:
                    continue
                f.write(self._BISK_ENTRY_STRUCT.pack(tid, off, length))

            f.flush()
            os.fsync(f.fileno())

        tmp_path.replace(self.bisk_path)
        self._bisk_index = None

    def _bisk_load_index(self) -> dict[int, tuple[int, int]]:
        """
        Load BISK index table into memory as a dict: id -> (offset, length).
        Assumes the .bisk is already validated.
        """
        if self._bisk_index is not None:
            return self._bisk_index

        with self.bisk_path.open("rb") as f:
            header_data = f.read(self._BISK_HEADER_STRUCT.size)
            (
                magic,
                version,
                flags,
                task_count,
                idx_off,
                idx_size,
                pay_off,
                pay_size,
                task_size,
                task_mtime,
            ) = self._BISK_HEADER_STRUCT.unpack(header_data)

            f.seek(idx_off)
            buf = f.read(idx_size)

        index: dict[int, tuple[int, int]] = {}
        pos = 0
        for _ in range(task_count):
            entry = buf[pos : pos + self._BISK_ENTRY_STRUCT.size]
            if len(entry) != self._BISK_ENTRY_STRUCT.size:
                break
            task_id, offset, length = self._BISK_ENTRY_STRUCT.unpack(entry)
            index[int(task_id)] = (int(offset), int(length))
            pos += self._BISK_ENTRY_STRUCT.size

        self._bisk_index = index
        return index

    def _bisk_lookup_block(self, task_id: int) -> Optional[str]:
        """
        Return the raw text block for the given task_id using BISK index.
        """
        if not self._bisk_is_valid():
            return None

        index = self._bisk_load_index()
        info = index.get(task_id)
        if info is None:
            return None

        offset, length = info
        with self.path.open("rb") as f:
            f.seek(offset)
            raw = f.read(length)

        return raw.decode("utf-8", errors="replace")

    def _bisk_is_valid(self) -> bool:
        """
        Check if .bisk file exists and matches current .task file.
        """
        if not self.bisk_path.exists():
            return False

        try:
            with self.bisk_path.open("rb") as f:
                header_data = f.read(self._BISK_HEADER_STRUCT.size)
                if len(header_data) != self._BISK_HEADER_STRUCT.size:
                    return False

                (
                    magic,
                    version_,
                    flags,
                    task_count,
                    idx_off,
                    idx_size,
                    pay_off,
                    pay_size,
                    task_size,
                    task_mtime,
                ) = self._BISK_HEADER_STRUCT.unpack(header_data)

            if magic != self.BISK_MAGIC:
                return False
            if version_ != self.BISK_VERSION:
                return False

            cur_size, cur_mtime = self._task_file_stats()
            if task_size != cur_size or task_mtime != cur_mtime:
                return False

            return True
        except OSError:
            return False

    def _load(self) -> list[Task]:
        # check if the .task file changed (mtime or size)
        if self._cache is not None:
            cur_stats = self._task_file_stats()
            if cur_stats != self._task_stats:
                # file changed => invalidate cache and bisk/index
                self._cache = None
                self._bisk_valid = False
                self._index_valid = False
                self._load_index()  # rebuild .task.index
                self._bisk_build()  # rebuild .bisk

        # load fresh data if needed
        if self._cache is None:
            blocks = self._read_blocks()
            self._cache = [Task.parse(b) for b in blocks]
            self._task_stats = self._task_file_stats()

        return sorted(self._cache, key=lambda t: t.num)

    def _write_grouped(self, tasks: list[Task]) -> None:
        groups: dict[Optional[str], list[Task]] = {}
        no_group: list[Task] = []
        index: dict[int, int] = {}

        for t in tasks:
            if t.group:
                groups.setdefault(t.group, []).append(t)
            else:
                no_group.append(t)

        with open(self.path, "w", encoding="utf-8") as f:
            f.write(self.HEADER)

            for group, g_tasks in groups.items():
                for t in g_tasks:
                    offset = f.tell()
                    f.write(t.serialize())
                    f.write("\n")
                    index[t.num] = offset

            for t in no_group:
                offset = f.tell()
                f.write(t.serialize())
                f.write("\n")
                index[t.num] = offset

        with open(self.index_path, "w", encoding="utf-8") as idx_file:
            for k, v in index.items():
                idx_file.write(f"{k}:{v}\n")

        self._index = index
        self._cache = None

        # 🆕 بعد از هر نوشتن، BISK را rebuild کن
        try:
            self._bisk_build()
        except Exception:
            self._bisk_index = None

    def _read_blocks(self) -> list[str]:
        content = self.path.read_text(encoding="utf-8")

        blocks: list[str] = []
        current: list[str] = []
        last_group: str | None = None

        for line in content.splitlines():
            stripped = line.strip()

            if not stripped or stripped.startswith("$$"):
                continue

            # group line
            if stripped.startswith("[") and stripped.endswith("]"):
                last_group = line
                continue

            # start new task
            if stripped.startswith("@task"):
                if current:
                    blocks.append("\n".join(current))
                    current = []

                if last_group:
                    current.append(last_group)
                    last_group = None

            current.append(line)

        if current:
            blocks.append("\n".join(current))

        return blocks

    def _next_id(self) -> int:
        tasks = self.list_tasks()
        if not tasks:
            return 1
        return max(t.num for t in tasks) + 1

    def list_tasks(self) -> list[Task]:
        return list(self._load())

    def add(
        self,
        name: str,
        start: str | time,
        end: str | time,
        desc: Optional[str] | None = None,
        group: Optional[str] | None = None
    ) -> Task:
        """
        add Task object in file `.task`.
        """
        tasks = self.list_tasks()
        num = self._next_id()
        date = datetime.now().strftime("%y-%m-%d")
        start_t = start
        end_t = end

        if isinstance(name, int):
            name = str(name)

        if end <= start:
            start_t, end_t = end, start

        task = Task(
            num=num, name=name, start=start_t, end=end_t, created_date=date, done=False, desc=desc, group=group
        )

        task._normalize_time

        tasks.append(task)
        self._write_grouped(tasks)
        return task

    def exists(self, num: int) -> bool:
        """
        Check existed on Task on `.task` file
        
        ----------------------
        Args:
            num: Number of Task(id).
        * exsist Added on `v1.2`
        """
        tasks = self.list_tasks()
        for t in tasks:
            if t.num == num:
                return True
        return False

    def add_custom(self, num: int, key: str, value: Union[str, dict, list, int, float]) -> None:
        """
        Add or update a custom metadata field for a task.
        """

        if not isinstance(key, str):
            raise TaskValueError("custom key must be str")

        tasks = self.list_tasks()

        target = None
        for t in tasks:
            if t.num == num:
                target = t
                break

        if target is None:
            raise TaskError(f"Task {num} not found.")

        target.custom[key] = value

        self._write_grouped(tasks)

    def add_custom_bulk(self, num: int, **data) -> None:
        """
        Add multiple custom metadata fields to a task.
        """

        tasks = self.list_tasks()

        target = None
        for t in tasks:
            if t.num == num:
                target = t
                break

        if target is None:
            raise TaskError(f"Task {num} not found.")

        for k, v in data.items():
            if not isinstance(k, str):
                raise TaskValueError("custom key must be str")

            target.custom[k] = v

        self._write_grouped(tasks)

    def get_custom(self, num: int, key: str, default=None):
        """
        Get a custom metadata value from a task.
        """

        task = self.get(num)

        if task is None:
            raise TaskError(f"Task {num} not found.")

        return task.custom.get(key, default)

    def remove_custom(self, num: int, key: str) -> None:
        """
        Remove a custom metadata field from a task.
        """

        tasks = self.list_tasks()

        target = None
        for t in tasks:
            if t.num == num:
                target = t
                break

        if target is None:
            raise TaskError(f"Task {num} not found.")

        if key not in target.custom:
            raise TaskError(f"Custom field '{key}' not found in task {num}.")

        del target.custom[key]

        self._write_grouped(tasks)

    def edit(self, num: int, **fields) -> bool:
        tasks = self._load()
        found = False

        for t in tasks:
            if t.num != num:
                continue

            found = True

            for k, v in fields.items():
                if v is None:
                    continue

                if k == "complete":
                    t.done = bool(v)
                elif hasattr(t, k):
                    setattr(t, k, v)

        if found:
            self._write_grouped(tasks)

        return found

    def complete(self, num: int) -> bool:
        tasks = self.list_tasks()
        found = False

        for t in tasks:
            if t.num == num:
                t.done = True
                found = True

        self._write_grouped(tasks)
        return found


    def remove(self, num: int) -> bool:
        tasks = self._load()
        new_tasks = [t for t in tasks if t.num != num]

        removed = len(tasks) != len(new_tasks)

        if removed:
            self._write_grouped(new_tasks)

        return removed

    # ---------------------------------
    # Group field (Added in v1.3)
    # ---------------------------------

    def add_group(self, name: str, *ids: int) -> Task:
        """
        add group of Tasks

        -------------------
        Args:
            name(str): name of Group
            args(int): Number of Tasks
        Example:
            ```python
            from taskmg import TaskRepo

            repo = TaskRepo(Path)
            ```
        * Group Added on `v1.3`
        """
        tasks = self._load()

        for t in tasks:
            if t.num in ids:
                t.group = name

        return t

        self._write_grouped(tasks)

    def remove_group_from_task(self, num: int) -> None:
        tasks = self._load()

        for t in tasks:
            if t.num == num:
                del t.group

    def list_groups(self) -> list[str]:
        """
        show List of Groups

        ------------------------
        Example:
            ```python
            repo.list_groups()
            ```
            ***output:***
            ```python
            ['work','study','gym']
            ```
        * Group Added on `v1.3`
        """
        groups = {t.group for t in self.list_tasks() if t.group}
        return sorted(groups, key=lambda t: t.num)

    def get_group(self, name: str) -> list[Task]:
        """
        show of datas of Tasks in Group

        ----------------------------------
        Args:
            name(str): name of Group
        Example:
            ```python
            repo.get_group("work")
            ```
            ***output:***
            ```python
            [
             Task(1,"coding",...),
             Task(4,"deploy",...)
            ]
            ```
        * Group Added on `v1.3`
        """
        return [t for t in self._load() if t.group == name]

    def remove_group(self, name: str) -> None:
        """
        Remove group from `.task` file

        -----------------------
        Args:
            name(str): name of Group
        Example:
            ```python
            repo.remove_group("work")
            ```
        * Group Added on `v1.3`
        """
        tasks = self._load()

        for t in tasks:
            if t.group == name:
                t.group = None

        self._write_grouped(tasks)

    def edit_in_group(
        self,
        name: str,
        target: Literal["name","start","end","desc","done"],
        value: Union[str,bool,time]
    ) -> None:
        """
        edit of data Tasks on Group

        ---------------------------------
        Args:
            name(str): name of groups
            target(str): target of data for add in task(data, desc)
            value: Value of data
        * Group Added on `v1.3`
        """
        tasks = self.list_tasks()
        value_oky = False
        target_oky = False

        for t in tasks:

            if t.group != name:
                continue

            if target == "name" and isinstance(value, str):
                value_oky = True
                target_oky = True
                t.name = name

            elif target == "start" and isinstance(value, time):
                value_oky = True
                target_oky = True
                value = value.strftime("%H:%M")
                t.start = value

            elif target == "end" and isinstance(value, time):
                value_oky = True
                target_oky = True
                value = value.strftime("%H:%M")
                t.end = value

            elif target == "desc" and isinstance(value, str):
                value_oky = True
                target_oky = True
                t.desc = value

            elif target == "done" and isinstance(value, bool):
                value_oky = True
                target_oky = True
                t.done = value

            else:
                if not value_oky:
                    vpromt = "value is wrong"
                else:
                    vpromt = ""

                if not target_oky:
                    tpromt = f"target is 'name','start','end','desc','done'. not '{target}'"
                else:
                    tpromt = ""
                
                if tpromt == "" and vpromt == "":
                    vpromt += " and "
                
                raise TaskValueError(tpromt, vpromt)

        self._write_grouped(tasks)
    
    def add_task_in_group(self, name: str, task: Task) -> Task:
        """
        Add Task in Group

        --------------------
        Args:
            name(str): Name of Group
            task(Task): Task for add to Group
        * Group Added on `v1.3`
        """
        tasks = self.list_tasks()

        task.group = name
        task.num = self._next_id()

        tasks.append(task)

        self._write_grouped(tasks)

        return task
      
    # ============================================ helper functions ============================================

    def clear(self) -> None:
        """clear of files(remove of Tasks)."""
        with open(self.path, "w") as clear:
            clear.write("")
            clear.seek(0)
            clear.write(self.HEADER)
        with open(self.bisk_path, "wd") as clear:
            clear.write("")
            clear.seek(0)
            clear.write(self.BISK_MAGIC)

        open(self.index_path, "w").write("")

    def remove_files(self) -> None:
        os.remove(self.path)
        os.remove(self.index_path)
        os.remove(self.bisk_path)

    def search(self, **kwargs) -> int | None:
        """
        Search for a task matching multiple fields.

        --------------------------------------------
        Args:
            **kwargs: name(str), start(str), end(str) and...
        ----------------------
        Example:
            ```
            repo.search(name="coding", end="12:00")
            ```
        * search Added on `v1.2`
        """
        for task in self.list_tasks():
            if all(str(getattr(task, k, None)) == str(v) for k, v in kwargs.items()):
                return task.num
        return None

    def add_sample(self) -> None:
        """
        add 3 Task for **example**.
        * add_sample Added on `v1.1`
        """
        self.add("coding", "12:00", "13:00")
        self.add("workout", "13:15", "14:00")
        self.add("learn a TaskRepo", "15:00", "15:00")

    def get(self, num: int) -> Task | None:
        """
        Return Task object for the given id.
        Uses BISK if available, then textual index, then full scan.
        """
        # 1) تلاش با BISK
        raw = self._bisk_lookup_block(num)
        if raw is not None:
            return Task.parse(raw)

        # 2) تلاش با ایندکس متنی
        if not self._index:
            self._load_index()

        offset = self._index.get(num)
        if offset is not None:
            with open(self.path, "r", encoding="utf-8") as f:
                f.seek(offset)

                block_lines: list[str] = []
                for line in f:
                    if line.startswith("@task") and block_lines:
                        break
                    block_lines.append(line)

            if block_lines:
                return Task.parse("".join(block_lines))

        # 3) fallback: جستجوی کامل
        for t in self.list_tasks():
            if t.num == num:
                return t

        return None

    def return_task(self, num: int, output: bool= False) -> Task:
        """
        Return a task either as structured data or serialized text.

        ---------------------------------------
        Args:
            num (int): Number of task(id).
            output:
                `true` => Return Task object
                `false` => Return block of Task
        ---------------------------------
        Returns:
            Taskobj
            Block
        * return_task Added on `v1.1`
        """
        for t in self.list_tasks():
            if t.num == num:
                if output:
                    return {
                        "name": t.name,
                        "start": t.start,
                        "end": t.end,
                        "created_date": t.created_date,
                        "done": t.done,
                        "desc": t.desc,
                    }
                elif output == "ret_block":
                    return t.serialize()
                else:
                    return t
        return None

    def filter(self, **kwargs) -> list[Task]:
        tasks = self._load()

        result = []

        for t in tasks:
            ok = True

            for k, v in kwargs.items():
                if getattr(t, k, None) != v:
                    ok = False
                    break

            if ok:
                result.append(t)

        return result


class _TaskProxy:
    def __init__(self, repo, task):
        self._repo = repo      # reference to TaskRepo
        self._task = task      # actual Task object

    def __getattr__(self, key):
        return getattr(self._task, key)

    def __setattr__(self, key, value):
        # برای attribute های خصوصی
        if key.startswith("_"):
            return super().__setattr__(key, value)

        # ارسال تغییر به Repo
        self._repo.edit(self._task.num, **{key: value})

        # آپدیت داده‌ها
        setattr(self._task, key, value)

    def __delattr__(self, key):
        if key.startswith("_"):
            super().__delattr__(key)
            return

        # اطلاع به repo
        self._repo.edit(self._task.num, **{key: None})

        # آپدیت آبجکت در حافظه
        if hasattr(self._task, key):
            setattr(self._task, key, None)
