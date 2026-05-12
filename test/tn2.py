import pytest
from typer.testing import CliRunner
from taskCLI import cli
from taskrepo import TaskRepo

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def repo_file(tmp_path):
    return tmp_path / "tasks.task"


@pytest.fixture
def patch_repo(monkeypatch, repo_file):
    def fake_repo():
        return TaskRepo(str(repo_file))

    monkeypatch.setattr("taskCLI.get_repo", fake_repo)


# ---------------- ADD ----------------


def test_add_task(runner, patch_repo):
    result = runner.invoke(cli, ["add", "gym", "10:00", "11:00"])

    assert result.exit_code == 0
    assert "Added Task" in result.output


# ---------------- LIST ----------------


def test_list_empty(runner, patch_repo):
    result = runner.invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "No tasks" in result.output


def test_list_after_add(runner, patch_repo):
    runner.invoke(cli, ["add", "gym", "10:00", "11:00"])
    result = runner.invoke(cli, ["list"])

    assert "gym" in result.output


# ---------------- COMPLETE ----------------


def test_complete_task(runner, patch_repo):
    runner.invoke(cli, ["add", "gym", "10:00", "11:00"])
    result = runner.invoke(cli, ["complete", "1"])

    assert result.exit_code == 0
    assert "completed" in result.output


# ---------------- REMOVE ----------------


def test_remove_task(runner, patch_repo):
    runner.invoke(cli, ["add", "gym", "10:00", "11:00"])
    result = runner.invoke(cli, ["remove", "1"])

    assert result.exit_code == 0
    assert "removed" in result.output


# ---------------- SHOW ----------------


def test_show_task(runner, patch_repo):
    runner.invoke(cli, ["add", "gym", "10:00", "11:00"])
    result = runner.invoke(cli, ["show", "1"])

    print(result.output)
    assert result.exit_code == 0
    assert "gym" in result.output


# ---------------- OUTPUT ----------------


def test_output_name(runner, patch_repo):
    runner.invoke(cli, ["add", "gym", "10:00", "11:00"])
    result = runner.invoke(cli, ["output", "1", "name"])

    assert result.exit_code == 0
    assert "gym" in result.output


# ---------------- FIND ----------------


def test_find_task(runner, patch_repo):
    runner.invoke(cli, ["add", "gym", "10:00", "11:00"])
    result = runner.invoke(cli, ["find", "gym", "10:00", "11:00", "false"])

    assert result.exit_code == 0
