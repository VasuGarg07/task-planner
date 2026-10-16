import { Check, Trash2, X } from "lucide-react";
import { useState } from "react";

import {
  type User,
  assignTask,
  deleteTask,
  getTask,
  setStoryPoints,
} from "./api";
import { useLoad } from "./useLoad";
import { userName } from "./userName";

interface Props {
  email: string;
  taskId: number;
  users: User[];
  onChange: () => void;
  onClose: () => void;
}

export default function TaskPanel({ email, taskId, users, onChange, onClose }: Props) {
  const [points, setPoints] = useState("");
  const { data: task, error, run } = useLoad(() => getTask(email, taskId), [email, taskId]);

  return (
    <div className="card panel">
      <div className="row title-row">
        <h2>{task === null ? "Task" : task.name}</h2>
        <button onClick={onClose}>
          <X size={16} /> Close
        </button>
      </div>
      {error !== "" && <p className="error">{error}</p>}

      {task !== null && (
        <>
          <p className="muted">{task.description === "" ? "No description" : task.description}</p>
          <p className="muted">
            Reporter: {userName(users, task.reporter_id, "nobody")} · Created{" "}
            {new Date(task.created_at).toLocaleString()} · Sprint:{" "}
            {task.sprint_id === null ? "none" : task.sprint_id}
          </p>
          <div className="row">
            <label>
              Assignee{" "}
              <select
                value={task.assignee_id === null ? "" : task.assignee_id}
                onChange={(event) =>
                  void run(async () => {
                    await assignTask(email, task.id, Number(event.target.value));
                    onChange();
                  })
                }
              >
                <option value="" disabled>
                  Unassigned
                </option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.username}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Story points{" "}
              <input
                type="number"
                min="0"
                value={points}
                placeholder={String(task.story_points)}
                onChange={(event) => setPoints(event.target.value)}
              />
            </label>
            <button
              disabled={points === ""}
              onClick={() =>
                void run(async () => {
                  await setStoryPoints(email, task.id, Number(points));
                  setPoints("");
                  onChange();
                })
              }
            >
              <Check size={16} /> Set points
            </button>
            <button
              className="danger"
              onClick={() =>
                void run(async () => {
                  await deleteTask(email, task.id);
                  onChange();
                  onClose();
                })
              }
            >
              <Trash2 size={16} /> Delete task
            </button>
          </div>
        </>
      )}
    </div>
  );
}
