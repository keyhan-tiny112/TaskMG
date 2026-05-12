# src/__init__.py
from repo import TaskRepo, Task, TaskError
from api import app, file, repo, TaskModel, StatusConfig
import types
import sys

__all__ = ["TaskModel", "StatusConfig"]

module = types.ModuleType("api.attrs")

def __API__():
    return app

def file_path():
    return file

api_attr.__module__ = "api.attrs"

ret_file_path.__module__ = "api.attrs"

module.api_attr = __API__

module.ret_file_path = file_path

sys.modules["api.attrs"] = module

__all__ = ["TaskRepo", "Task", "TaskError"]#, "Taskinfo"]

__version__ = "1.5"

__anchor__ = "keyhan"
__license__ = "Apache-v2.0"
__APIs__ = "python module: TaskRepo | server API: localhost:1212 for doc: localhost:1212/docs or localhost:1212/redocs"
__host__ = "localhost:800"
__suffixs__ = ".task: main storage file\n .bisk: task + binary, a powerfull cache for performance and speed of parsing.\n.task.index: index if all task. e.g. 1:20 | 1 -> number of task, 20 -> byte of task"
__github__ = "github.com/..."
