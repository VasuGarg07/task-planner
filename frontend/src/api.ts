export const PAGE_SIZE = 10;

export const ROLES = ["BA", "DEV", "QA", "PM", "DEV-OPS"] as const;
export const PROJECT_STATUSES = [
  "NOT STARTED",
  "DISCOVERY",
  "IN PROGRESS",
  "ON HOLD",
  "COMPLETED",
  "DROPPED",
] as const;
export const TASK_STATUSES = [
  "OPEN",
  "IN PROGRESS",
  "ON HOLD",
  "DONE",
  "VOID",
] as const;
export const SPRINT_STATUSES = ["PLANNING", "ACTIVE", "COMPLETED"] as const;

export type Role = (typeof ROLES)[number];
export type ProjectStatus = (typeof PROJECT_STATUSES)[number];
export type TaskStatus = (typeof TASK_STATUSES)[number];
export type SprintStatus = (typeof SPRINT_STATUSES)[number];

export interface Health {
  status: string;
  database: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  status: ProjectStatus;
}

export interface Task {
  id: number;
  project_id: number;
  name: string;
  description: string;
  reporter_id: number | null;
  assignee_id: number | null;
  created_at: string;
  status: TaskStatus;
  sprint_id: number | null;
  story_points: number;
}

export interface Sprint {
  id: number;
  project_id: number;
  name: string;
  start_date: string;
  end_date: string;
  max_capacity: number;
  status: SprintStatus;
}

export interface SprintLoad extends Sprint {
  current_capacity: number;
}

export interface WorkloadEntry {
  id: number;
  username: string;
  task_count: number;
}

export interface WorkloadReport {
  project_id: number;
  workload_report: Record<string, WorkloadEntry[]>;
}

export interface Log {
  id: number;
  created_at: string;
  project_id: number | null;
  actor_id: number | null;
  subject_type: string;
  subject_id: number;
  action_type: string;
  change_record: unknown;
}

export function errorMessage(caught: unknown): string {
  return caught instanceof Error ? caught.message : "Something went wrong.";
}

async function readFailure(response: Response): Promise<string> {
  const failure = (await response.json().catch(() => null)) as {
    detail?: unknown;
  } | null;
  const detail = failure?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const first = detail[0] as { msg?: unknown } | undefined;
    if (typeof first?.msg === "string") return first.msg;
  }
  return `Request failed (${response.status})`;
}

async function call(
  path: string,
  email: string,
  method: string,
  body?: object,
): Promise<Response> {
  const response = await fetch(`/api${path}`, {
    method,
    headers: { "Content-Type": "application/json", "X-User-Email": email },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) throw new Error(await readFailure(response));
  return response;
}

async function request<T>(
  path: string,
  email: string,
  method = "GET",
  body?: object,
): Promise<T> {
  const response = await call(path, email, method, body);
  return (await response.json()) as T;
}

async function send(path: string, email: string, method: string): Promise<void> {
  await call(path, email, method);
}

export function getHealth(): Promise<Health> {
  return request("/health", "");
}

export function getAllUsers(): Promise<User[]> {
  return request("/users?pageSize=100", "");
}

export function getUsers(page: number): Promise<User[]> {
  return request(`/users?page=${page}&pageSize=${PAGE_SIZE}`, "");
}

export function createUser(body: {
  username: string;
  email: string;
  role: Role;
}): Promise<User> {
  return request("/users", "", "POST", body);
}

export function deleteUser(id: number): Promise<void> {
  return send(`/users/${id}`, "", "DELETE");
}

export function getProjects(
  email: string,
  page: number,
  status: ProjectStatus | "",
): Promise<Project[]> {
  const filter = status === "" ? "" : `&status=${encodeURIComponent(status)}`;
  return request(`/projects?page=${page}&pageSize=${PAGE_SIZE}${filter}`, email);
}

export function getProject(email: string, id: number): Promise<Project> {
  return request(`/projects/${id}`, email);
}

export function createProject(
  email: string,
  body: { name: string; description: string },
): Promise<Project> {
  return request("/projects", email, "POST", body);
}

export function deleteProject(email: string, id: number): Promise<void> {
  return send(`/projects/${id}`, email, "DELETE");
}

export function setProjectStatus(
  email: string,
  id: number,
  status: ProjectStatus,
): Promise<Project> {
  return request(`/projects/${id}/status`, email, "PATCH", { status });
}

export function getLogs(email: string, projectId: number): Promise<Log[]> {
  return request(`/projects/${projectId}/logs`, email);
}

export function getSprintReport(
  email: string,
  projectId: number,
): Promise<SprintLoad[]> {
  return request(`/projects/${projectId}/sprint-report`, email);
}

export function getWorkload(
  email: string,
  projectId: number,
): Promise<WorkloadReport> {
  return request(`/projects/${projectId}/workload-report`, email);
}

export function getTasks(email: string, projectId: number): Promise<Task[]> {
  return request(`/tasks?projectId=${projectId}&pageSize=100`, email);
}

export function getTask(email: string, id: number): Promise<Task> {
  return request(`/tasks/${id}`, email);
}

export function createTask(
  email: string,
  body: {
    project_id: number;
    name: string;
    description: string;
    assignee_id: number | null;
  },
): Promise<Task> {
  return request("/tasks", email, "POST", body);
}

export function deleteTask(email: string, id: number): Promise<void> {
  return send(`/tasks/${id}`, email, "DELETE");
}

export function assignTask(
  email: string,
  id: number,
  assigneeId: number,
): Promise<Task> {
  return request(`/tasks/${id}/assign`, email, "PATCH", {
    assignee_id: assigneeId,
  });
}

export function moveTask(
  email: string,
  id: number,
  status: TaskStatus,
): Promise<Task> {
  return request(`/tasks/${id}/status`, email, "PATCH", { status });
}

export function setStoryPoints(
  email: string,
  id: number,
  storyPoints: number,
): Promise<Task> {
  return request(`/tasks/${id}/story-points`, email, "PATCH", {
    story_points: storyPoints,
  });
}

export function createSprint(
  email: string,
  body: {
    project_id: number;
    name: string;
    start_date: string;
    end_date: string;
    max_capacity: number;
  },
): Promise<Sprint> {
  return request("/sprints", email, "POST", body);
}

export function getSprint(email: string, id: number): Promise<Sprint> {
  return request(`/sprints/${id}`, email);
}

export function getSprintWeight(
  email: string,
  id: number,
): Promise<{ current_weight: number }> {
  return request(`/sprints/${id}/current-weight`, email);
}

export function addTaskToSprint(
  email: string,
  sprintId: number,
  taskId: number,
): Promise<Task> {
  return request(`/sprints/${sprintId}/add-task`, email, "PATCH", {
    task_id: taskId,
  });
}

export function setSprintStatus(
  email: string,
  id: number,
  status: SprintStatus,
): Promise<Sprint> {
  return request(`/sprints/${id}/status`, email, "PATCH", { status });
}
