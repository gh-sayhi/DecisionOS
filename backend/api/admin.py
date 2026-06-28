from __future__ import annotations

import os
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from backend.core.schemas import (
    AdminSummary,
    Actor,
    ActorInput,
    Creator,
    CreatorInput,
    LogEntry,
    LoginRequest,
    LoginResponse,
    ProjectRecord,
    ReportFile,
)
from backend.services.storage import (
    append_log,
    clear_logs,
    count_logs,
    create_actor,
    create_creator,
    delete_actor,
    delete_creator,
    list_reports,
    get_project,
    list_projects,
    list_logs,
    load_actors,
    load_creators,
    update_actor,
    update_creator,
)


router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-admin-token")


def require_admin(authorization: Annotated[str | None, Header()] = None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing admin token")
    token = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    valid_user = secrets.compare_digest(payload.username, ADMIN_USERNAME)
    valid_password = secrets.compare_digest(payload.password, ADMIN_PASSWORD)
    if not valid_user or not valid_password:
        append_log(
            "admin.login.failed",
            f"管理员登录失败: {payload.username}",
            actor=payload.username,
            level="warning",
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    append_log("admin.login.success", "管理员登录成功", actor=ADMIN_USERNAME)
    return LoginResponse(access_token=ADMIN_TOKEN, username=ADMIN_USERNAME)


@router.get("/summary", response_model=AdminSummary, dependencies=[Depends(require_admin)])
def summary() -> AdminSummary:
    creators = load_creators()
    actors = load_actors()
    return AdminSummary(
        creators=len(creators),
        actors=len(actors),
        reports=len(list_reports()),
        projects=len(list_projects()),
        logs=count_logs(),
        total_followers=sum(creator.followers for creator in creators) + sum(actor.followers for actor in actors),
    )


@router.get("/creators", response_model=list[Creator], dependencies=[Depends(require_admin)])
def get_creators() -> list[Creator]:
    return load_creators()


@router.post("/creators", response_model=Creator, dependencies=[Depends(require_admin)])
def post_creator(payload: CreatorInput) -> Creator:
    return create_creator(payload)


@router.put("/creators/{creator_id}", response_model=Creator, dependencies=[Depends(require_admin)])
def put_creator(creator_id: str, payload: CreatorInput) -> Creator:
    creator = update_creator(creator_id, payload)
    if creator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")
    return creator


@router.delete("/creators/{creator_id}", dependencies=[Depends(require_admin)])
def remove_creator(creator_id: str) -> dict[str, bool]:
    deleted = delete_creator(creator_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")
    return {"deleted": True}


@router.get("/actors", response_model=list[Actor], dependencies=[Depends(require_admin)])
def get_actors() -> list[Actor]:
    return load_actors()


@router.post("/actors", response_model=Actor, dependencies=[Depends(require_admin)])
def post_actor(payload: ActorInput) -> Actor:
    return create_actor(payload)


@router.put("/actors/{actor_id}", response_model=Actor, dependencies=[Depends(require_admin)])
def put_actor(actor_id: str, payload: ActorInput) -> Actor:
    actor = update_actor(actor_id, payload)
    if actor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")
    return actor


@router.delete("/actors/{actor_id}", dependencies=[Depends(require_admin)])
def remove_actor(actor_id: str) -> dict[str, bool]:
    deleted = delete_actor(actor_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")
    return {"deleted": True}


@router.get("/reports", response_model=list[ReportFile], dependencies=[Depends(require_admin)])
def reports() -> list[ReportFile]:
    return list_reports()


@router.get("/projects", response_model=list[ProjectRecord], dependencies=[Depends(require_admin)])
def projects() -> list[ProjectRecord]:
    return list_projects()


@router.get("/projects/{project_id}", response_model=ProjectRecord, dependencies=[Depends(require_admin)])
def project_detail(project_id: str) -> ProjectRecord:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("/logs", response_model=list[LogEntry], dependencies=[Depends(require_admin)])
def logs(
    limit: int = Query(default=200, ge=1, le=1000),
    event: str | None = None,
    level: str | None = None,
) -> list[LogEntry]:
    return list_logs(limit=limit, event=event, level=level)


@router.delete("/logs", dependencies=[Depends(require_admin)])
def remove_logs() -> dict[str, bool]:
    clear_logs(actor=ADMIN_USERNAME)
    return {"cleared": True}
