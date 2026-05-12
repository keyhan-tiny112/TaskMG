# src/api.py
# ---
# TaskMG  
# Copyright 2026 Keyhan

# This product includes software developed by Keyhan 
# for the TaskMG project.

# Licensed under the Apache License, Version 2.0.
# See the LICENSE file for full details
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from repo import (
    TaskRepo,
    TaskError,
    TaskParseError,
    TaskTimeError,
    TaskValueError
)
from annotated_doc import Doc
from annotated_types import Annotated
from typing import (
    Union,
    ReadOnly,
    Literal,
    Optional,
    Dict,
    TypedDict
)
from datetime import time
from pathlib import Path
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.exceptions import StarletteHTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

file = Path("Config/config.task")

repo = TaskRepo(file)

app = FastAPI(
    debug=True,
    title="Taskmg API",
    description="taskmg is a lightweight task manager built around a simple, fast and human-readable file format called '.task'.",
    version="1.5",
    openapi_url="Taskmg/openapi.json",
    redoc_url="Taskmg/ReDoc",
    docs_url="Taskmg/Doc"
)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.middleware("http")
async def lowercase_paths(request: Request, call_next):
    request.scope["path"] = request.scope["path"].lower()
    return await call_next(request)

# connecting to Rebis
@app.on_event("startup")
async def startup():
    r = redis.from_url("redis://localhost:6379")
    await FastAPILimiter.init(r)

# for add openapi.yaml
@app.get("Taskmg/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_json = app.openapi()
    yaml_output = yaml.dump(openapi_json, allow_unicode=True, sort_keys=False)
    return Response(content=yaml_output, media_type="application/x-yaml")

# limit rate
@app.get("/data", dependencies=[Depends(RateLimiter(times=1, seconds=3))])
async def get_data():
    return {"status": "ok"}

@app.exception_handler(StarletteHTTPException)
async def custom_rate_limiter_handler(request, exc):
    ip = request.client.host

    return JSONResponse(
        status_code=429,
        content={
            "ok": False,
            "err": "Rate limit exceeded",
            "desc": f"ip: {ip}",
        },
    )

# ======================================================
# Models
# ======================================================

class StatusConfig(TypedDict):
    ok: bool
    err: Optional[str]
    desc: Optional[str]

class TaskModel(BaseModel):
    """
    name: str
    start: Union[time, str]
    end: Union[time, str]
    created: Union[str, time]
    done: Union[bool, Literal["false", "true"]
    desc: Optional[str]
    custom: Optional[Dict[str, Union[int, float, list, dict, str]]]
    group: Optional[str]
    """
    name: str
    start: Annotated[Union[time, str], Doc("fromat: HH:MM. e.g. 09:05 or 23:20")]
    end: Annotated[Union[time, str], Doc("fromat: HH:MM. e.g. 09:05 or 23:20")]
    created: Annotated[Union[str, time], Doc("format: YYYY-MM-DD. e.g. 2026-10-21")]
    done: bool
    desc: Optional[str]
    custom: Annotated[Optional[Dict[str, Union[int, float, list, dict, str]]], Doc("e.g. {'key', 'value'} | {'key', ['value1', 'value2', 'value3']}")]
    group: Optional[str]

# ======================================================
# APIs
# ======================================================

# ------------------------- file -------------------------

@app.put("/taskmg/v1/config/", tags=['Task', 'file', 'edit'])
def set_path_file(path: str) -> StatusConfig:
    path = Path(path)
    if path.suffix != ".task":
        raise HTTPException(status_code=406, detail={"ok": False, "err": f"Path is '.task' file not {path.suffix}", "desc": f"Path:{path}"})
    if path.exists():
        global file
        file = path
        repo.path = file
        return {"ok": True, "desc": "Path set successfully"}
    else:
        raise HTTPException(status_code=400, detail={"ok": False, "err": "folder not found", "desc": f"Path:{path}"})

@app.get("/taskmg/v1/config/", tags=['Task', 'file', 'get'])
def get_path_file() -> str:
    return str(file.absolute())

# ------------------------- Taskmg -------------------------

@app.get("/taskmg/v1/credits",tags=['Taskmg', 'info'])
def credits_taskmg():
    return "keyhan and others."

@app.get("/taskmg/v1/help", tags=['Taskmg', 'info'])
def help_taskmg():
    return "Use 'Taskmg/v1/openAPI.yaml' or 'Taskmg/v1/openAPI.json'.\nand for Docs Use 'Taskmg/v1/Doc' or 'Taskmg/v1/Doc'."

@app.get("/taskmg/v1/readme", tags=['Taskmg', 'info'])

# ------------------------- TaskRepo -------------------------

@app.post("/taskrepo/v1/task/{Task_id}", tags=['Task', 'add'])
def add(Task_id: int, Task: TaskModel) -> StatusConfig:
    try:
        repo.add(name=Task_id, start=Task.start, end=Task.end, desc=Task.desc, group=Task.group)
    except TaskTimeError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": f"format is HH:MM. e.g. 09:05 or 23:20"})
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": f"Task(name: str, start: time -> HH:MM, end: time -> HH:MM, desc: Optinal -> str, group: Optinal -> str)"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})
    return {"ok": True, "desc": "Task created"}

@app.delete("/taskrepo/v1/tasks/{Task_id}", tags=['Task', 'remove'])
def remove(Task_id: int) -> StatusConfig:
    try:
        repo.remove(num=Task_id)
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": f"Task(num(id): int)"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})
    return {"ok": True}

@app.get("/taskrepo/v1/tasks", name="ListTask", tags=['Task', 'list', 'get'])
def lst() -> list[TaskModel] | StatusConfig:
    try:
        lst = []
        tasks = repo.list_tasks()
        for t in tasks:
            lst.append(TaskModel(id=t.num, ))
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.get("/taskrepo/v1/tasks/{Task_id}", tags=['Task', 'get'])
def get(Task_id: int) -> TaskModel | StatusConfig:
    try:
        task = repo.get(num=Task_id)
        return TaskModel(id=Task_id, name=task.name, start=task.start, end=task.end, created=task.created, done=task.done, desc=task.desc, group=task.group)
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": f"Task(name: str, start: time -> HH:MM, end: time -> HH:MM, desc: Optinal -> str, group: Optinal -> str)"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.post("/taskrepo/v1/tasks/{Task_id}/exists/", tags=['Task', 'exists'])
def exists(Task_id: int) -> bool | StatusConfig:
    try:
        return repo.exists(Task_id)
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": f"Task(num(id): int)"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.put("/taskrepo/v1/tasks/{Task_id}", tags=['Task', 'edit'])
def edit(Taskid: int, Task: TaskModel) -> bool | StatusConfig:
    try:
        if not repo.edit(Task_id, name=Task.name, start=Task.start, end=Task.end, created=Task.created, done=Task.done, desc=Task.desc, group=Task.group):
            raise HTTPException(status_code=400, detail={"ok": False, "err": "fail of editing.", "desc": "try again."})
        else:
            return {"ok": True, "desc": "edited Task"}
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": f"Task(num(id): int, name: str, start: time -> HH:MM, end: time -> HH:MM, desc: Optinal -> str, group: Optinal -> str)"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.patch("/taskrepo/v1/task/{Task_id}", tags=['Task', 'complete'])
def complete(Task_id: int) -> StatusConfig:
    try:
        repo.complete(Task_id)
        return {"ok": True, "desc": ""}
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": f"Task(num(id): int)"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.get("/teapot", description="this is a joke", tags=['joke'], include_in_schema=False)
def teapot() -> StatusConfig:
    raise HTTPException(status_code=418, detail={"ok": "Hmm... Wait... i don't know", "err": "I'm a teapot", "desc": "this is a joke. ok?!"})

@app.post("/taskrepo/v1/group/{name}", tags=['group', 'add'])
def add_group(name:str, id: int):
    try:
        repo.add_group(name, id)
        return {"ok": True, "desc": ""}
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "num(id): int and name: str"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.delete("/taskrepo/v1/group/{name}", tags=['group', 'remove'])
def del_group(name:str):
    try:
        repo.remove_group(name, id)
        return {"ok": True, "desc": ""}
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "name: str"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.get("/taskrepo/v1/group/{name}", tags=['group', 'get'])
def get_group(name: str):
    try:
        return repo.get_group(name)
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "name: str"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

@app.get("/taskrepo/v1/group/groups", tags=['group', 'list'])
def lst_group():
    try:
        return repo.list_groups()
    except TaskParseError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "file is ok?"})
    except TaskValueError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "name: str"})
    except TaskError as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e), "desc": "Error from taskmg."})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "err": str(e)})

