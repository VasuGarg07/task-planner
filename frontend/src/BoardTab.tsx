import { type FormEvent, useState } from "react";

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
    <section>
      <form className="row card" onSubmit={(event) => void handleCreate(event)}>
        <input placeholder="Task name" value={name} onChange={(event) => setName(event.target.value)} />
        <input placeholder="Description" value={description} onChange={(event) => setDescription(event.target.value)} />
        <select value={assignee} onChange={(event) => setAssignee(event.target.value)}>
          <option value="">Unassigned</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.username}
            </option>
          ))}
        </select>
        <button className="primary" type="submit">
          Add task
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
        {TASK_STATUSES.map((status) => (
          <div className="column card" key={status}>
            <h3>{status}</h3>
            {tasks
              .filter((task) => task.status === status)
              .map((task) => (
                <div className="task" key={task.id}>
                  <strong>{task.name}</strong>
                  <span className="muted">
                    {userName(users, task.assignee_id, "Unassigned")} · {task.story_points} pts
                  </span>
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
                  <button onClick={() => setOpenTaskId(task.id)}>Details</button>
                </div>
              ))}
          </div>
        ))}
      </div>
    </section>
  );
}
