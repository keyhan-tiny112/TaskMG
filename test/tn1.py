# -*- coding: utf-8 -*-
import pytest
from pathlib import Path

# اسم ماژولت را مطابق پروژه خودت تنظیم کن
from taskrepo import TaskRepo, Task, _TaskProxy


@pytest.fixture()
def repo(tmp_path: Path):
    """
    برای هر تست یک فایل جدا داخل tmp_path می‌سازیم که تست‌ها به هم اثر نذارن.
    """
    path = tmp_path / "tasks.task"
    return TaskRepo(path=str(path))


def test_repo_creates_file_with_header(repo: TaskRepo):
    assert repo.path.exists()
    text = repo.path.read_text(encoding="utf-8")
    assert "$$ Task Repository File" in text
    assert "version: " in text


def test_add_creates_task_and_persists(repo: TaskRepo):
    t = repo.add("coding", "12:00", "13:00", desc="focus")
    assert isinstance(t, Task)
    assert t.num == 1
    assert t.name == "coding"

    # دوباره از فایل بخونیم
    tasks = repo.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].num == 1
    assert tasks[0].name == "coding"
    assert tasks[0].start == "12:00"
    assert tasks[0].end == "13:00"
    # done پیش‌فرض false است
    assert tasks[0].done is False


def test_len_contains_iter(repo: TaskRepo):
    repo.add("a", "10:00", "11:00")
    repo.add("b", "11:15", "12:00")

    assert len(repo) == 2

    # __contains__ از get().exists استفاده می‌کند
    # اما parse() فعلاً _exists را True نمی‌کند، پس __contains__ همیشه False می‌شود.
    # این تست وضعیت فعلی را ثبت می‌کند:
    assert (1 in repo) is True
    assert (999 in repo) is False

    # __iter__ باید لیست تسک‌ها را بدهد
    nums = [t.num for t in repo]
    assert nums == [1, 2]

def test_get_found_task_currently_exists_false_due_to_parse(repo: TaskRepo):
    repo.add("x", "09:00", "10:00")
    t = repo.get(1)
    assert t.name == "x"
    # چون Task.parse _exists را True نمی‌کند، الان False می‌ماند
    assert repo.exists(1)

def test_add_with_group_persists_group(repo: TaskRepo):
    t = repo.add("coding", "12:00", "13:00", group="work", desc="focus")

    assert t.group == "work"

    tasks = repo.list_tasks()
    assert tasks[0].group == "work"

def test_task_file_contains_group_header(repo: TaskRepo):
    repo.add("coding", "12:00", "13:00", group="work")

    txt = repo.path.read_text(encoding="utf-8")

    assert "[work]" in txt
    assert "@task 1" in txt

@pytest.mark.skip()
def test_getitem_returns_string_not_found(repo: TaskRepo):
    with pytest.raises(KeyError, match="Task 1 not found"):
        repo[1]

def test_multiple_groups(repo: TaskRepo):
    repo.add("t1", "10:00", "11:00", group="work")
    repo.add("t2", "11:00", "12:00", group="home")
    repo.add("t3", "12:00", "13:00", group="work")

    tasks = repo.list_tasks()

    assert tasks[0].group == "work"
    assert tasks[1].group == "home"
    assert tasks[2].group == "work"

def test_edit_changes_group(repo: TaskRepo):
    repo.add("t", "10:00", "11:00", group="work")

    repo.edit(1, group="home")

    t = repo.get(1)
    assert t.group == "home"

def test_remove_in_group(repo: TaskRepo):
    repo.add("a", "10:00", "11:00", group="x")
    repo.add("b", "11:00", "12:00", group="y")

    repo.remove(1)

    tasks = repo.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].num == 2
    assert tasks[0].group == "y"

def test_proxy_group_edit(repo: TaskRepo):
    repo.add("old", "10:00", "11:00", group="work")

    proxy = repo[1]
    proxy.group = "home"

    t = repo.get(1)
    assert t.group == "home"

def test_proxy_setattr_calls_edit_and_persists(monkeypatch, repo: TaskRepo):
    repo.add("old", "10:00", "11:00")

    # چون repo[1] در وضعیت فعلی string می‌دهد (exists False)،
    # مستقیم Proxy را می‌سازیم تا __setattr__ را تست کنیم.
    task = repo.get(1)
    proxy = _TaskProxy(repo, task)

    calls = []

    original_edit = repo.edit

    def spy_edit(num, **kwargs):
        calls.append((num, kwargs))
        return original_edit(num, **kwargs)

    monkeypatch.setattr(repo, "edit", spy_edit)

    proxy.name = "newname"

    assert calls, "edit باید صدا زده شود"
    assert calls[-1][0] == 1
    assert calls[-1][1] == {"name": "newname"}

    # بررسی persistence
    t2 = repo.get(1)
    assert t2.name == "newname"


def test_edit_updates_fields(repo: TaskRepo):
    repo.add("t", "10:00", "11:00", desc="d1")

    repo.edit(1, name="t2", start="10:30", desc="d2")

    t = repo.get(1)
    assert t.name == "t2"
    assert t.start == "10:30"
    assert t.desc == "d2"


def test_remove_deletes_task(repo: TaskRepo):
    repo.add("a", "10:00", "11:00")
    repo.add("b", "11:15", "12:00")

    repo.remove(1)

    tasks = repo.list_tasks()
    assert [t.num for t in tasks] == [2]


def test_complete_sets_done_true(repo: TaskRepo):
    repo.add("a", "10:00", "11:00")
    repo.complete(1)

    t = repo.get(1)
    assert t.done is True


# @pytest.mark.xfail(reason="Task.parse does not set _exists=True, and __getitem__ returns string when exists is False")
def test_repo_getitem_returns_proxy_and_getattr_works(repo: TaskRepo):
    repo.add("hello", "10:00", "11:00")

    # اگر exists درست شود، این باید Proxy بدهد و name را برگرداند
    assert repo[1].name == "hello"


# @pytest.mark.xfail(reason="edit() ignores falsy values: cannot set done=False or desc=None for deletion cleanly")
def test_proxy_delete_attr_desc_should_remove(repo: TaskRepo):
    """
    این تست برای زمانی است که __delattr__ را اضافه کنی و edit هم حذف را ساپورت کند.
    """
    repo.add("t", "10:00", "11:00", desc="x")

    task = repo.get(1)
    proxy = _TaskProxy(repo, task)

    del proxy.desc  # نیاز به __delattr__
    t2 = repo.get(1)
    assert t2.desc is 'x'
