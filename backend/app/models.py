from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, JsonValue

Role = Literal["BA", "DEV", "QA", "PM", "DEV-OPS"]
ProjectStatus = Literal[
    "NOT STARTED", "DISCOVERY", "IN PROGRESS", "ON HOLD", "COMPLETED", "DROPPED"
]
TaskStatus = Literal["OPEN", "IN PROGRESS", "ON HOLD", "DONE", "VOID"]
SprintStatus = Literal["PLANNING", "ACTIVE", "COMPLETED"]
SubjectType = Literal["PROJECT", "SPRINT", "TASK"]
ActionType = Literal["CREATE", "UPDATE", "DELETE"]


class NewUser(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=100)
    role: Role = "BA"


class User(BaseModel):
    id: int
    username: str
    email: str
    role: Role


class NewProject(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class Project(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    status: ProjectStatus


class ProjectStatusChange(BaseModel):
    status: ProjectStatus


class NewTask(BaseModel):
    project_id: int
    name: str = Field(min_length=1)
    description: str = ""
    assignee_id: int | None = None


class Task(BaseModel):
    id: int
    project_id: int
    name: str
    description: str
    reporter_id: int | None
    assignee_id: int | None
    created_at: datetime
    status: TaskStatus
    sprint_id: int | None
    story_points: int


class TaskAssignment(BaseModel):
    assignee_id: int


class TaskStatusChange(BaseModel):
    status: TaskStatus


class TaskStoryPoints(BaseModel):
    story_points: int = Field(ge=0)


class NewSprint(BaseModel):
    project_id: int
    name: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date
    max_capacity: int = Field(gt=0)


class Sprint(BaseModel):
    id: int
    project_id: int
    name: str
    start_date: date
    end_date: date
    max_capacity: int
    status: SprintStatus


class SprintStatusChange(BaseModel):
    status: SprintStatus


class SprintTask(BaseModel):
    task_id: int


class SprintWeight(BaseModel):
    current_weight: int


class SprintLoad(Sprint):
    current_capacity: int


class WorkloadEntry(BaseModel):
    id: int
    username: str
    task_count: int


class WorkloadRow(WorkloadEntry):
    status: TaskStatus


class WorkloadReport(BaseModel):
    project_id: int
    workload_report: dict[str, list[WorkloadEntry]]


class Log(BaseModel):
    id: int
    created_at: datetime
    project_id: int | None
    actor_id: int | None
    subject_type: SubjectType
    subject_id: int
    action_type: ActionType
    change_record: JsonValue
