import { Info, Plus } from "lucide-react";
import { type FormEvent, useState } from "react";

import Avatar from "./Avatar";
import TaskPanel from "./TaskPanel";
import {
  TASK_STATUSES,
  type TaskStatus,
  type User,
  createTask,
  getTasks,
  moveTask,
} from "./api";
import { useLoad } from "./useLoad";
import { userName } from "./userName";

interface Props {
  email: string;
  projectId: number;
  users: User[];
}

export default function BoardTab({ email, projectId, users }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [assignee, setAssignee] = useState("");
  const [openTaskId, setOpenTaskId] = useState<number | null>(null);
  const { data, error, reload, run } = useLoad(
    () => getTasks(email, projectId),
    [email, projectId],
  );
  const tasks = data ?? [];

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    await run(async () => {
      await createTask(email, {
        project_id: projectId,
        name,
        description,
        assignee_id: assignee === "" ? null : Number(assignee),
      });
      setName("");
      setDescription("");
    });
  }

  return (
    <>
      <form className="card toolbar" onSubmit={(event) => void handleCreate(event)}>
        <input placeholder="Task name" value={name} onChange={(event) => setName(event.target.value)} />
        <input className="wide" placeholder="Description" value={description} onChange={(event) => setDescription(event.target.value)} />
        <select value={assignee} onChange={(event) => setAssignee(event.target.value)}>
          <option value="">Unassigned</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.username}
            </option>
          ))}
        </select>
        <button className="primary" type="submit">
          <Plus size={16} /> Add task
        </button>
      </form>

      {error !== "" && <p className="error">{error}</p>}

      {openTaskId !== null && (
        <TaskPanel
          email={email}
          taskId={openTaskId}
          users={users}
          onChange={reload}
          onClose={() => setOpenTaskId(null)}
        />
      )}

      <div className="board">
        {TASK_STATUSES.map((status) => {
          const column = tasks.filter((task) => task.status === status);
          return (
            <div className="column" data-status={status} key={status}>
              <h3>
                <span className="badge" data-status={status}>
                  {status}
                </span>
                <span className="count">{column.length}</span>
              </h3>
              {column.map((task) => (
                <div className="task" key={task.id}>
                  <strong>{task.name}</strong>
                  <div className="row task-meta">
                    <Avatar small name={userName(users, task.assignee_id, "?")} />
                    <span className="muted">{userName(users, task.assignee_id, "Unassigned")}</span>
                    <span className="points">{task.story_points} pts</span>
                  </div>
                  <select
                    value={task.status}
                    onChange={(event) =>
                      void run(() => moveTask(email, task.id, event.target.value as TaskStatus))
                    }
                  >
                    {TASK_STATUSES.map((option) => (
                      <option key={option}>{option}</option>
                    ))}
                  </select>
                  <button onClick={() => setOpenTaskId(task.id)}>
                    <Info size={16} /> Details
                  </button>
                </div>
              ))}
              {column.length === 0 && <p className="muted">No tasks</p>}
            </div>
          );
        })}
      </div>
    </>
  );
}
