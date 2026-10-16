import { Plus } from "lucide-react";
import { useState } from "react";

import {
  SPRINT_STATUSES,
  type SprintStatus,
  type Task,
  addTaskToSprint,
  getSprint,
  getSprintWeight,
  setSprintStatus,
} from "./api";
import { useLoad } from "./useLoad";

interface Props {
  email: string;
  sprintId: number;
  tasks: Task[];
  onChange: () => void;
}

export default function SprintDetail({ email, sprintId, tasks, onChange }: Props) {
  const [taskId, setTaskId] = useState("");
  const { data, error, run } = useLoad(async () => {
    const [sprint, weight] = await Promise.all([
      getSprint(email, sprintId),
      getSprintWeight(email, sprintId),
    ]);
    return { sprint, weight: weight.current_weight };
  }, [email, sprintId]);
  const inSprint = tasks.filter((task) => task.sprint_id === sprintId);
  const available = tasks.filter((task) => task.sprint_id !== sprintId);

  return (
    <div className="detail">
      {error !== "" && <p className="error">{error}</p>}
      {data !== null && (
        <>
          <p className="muted">
            Weight {data.weight} of {data.sprint.max_capacity} points
          </p>
          <div className="row">
            <label>
              Status{" "}
              <select
                value={data.sprint.status}
                onChange={(event) =>
                  void run(async () => {
                    await setSprintStatus(email, sprintId, event.target.value as SprintStatus);
                    onChange();
                  })
                }
              >
                {SPRINT_STATUSES.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            </label>
            <select value={taskId} onChange={(event) => setTaskId(event.target.value)}>
              <option value="">Add a task...</option>
              {available.map((task) => (
                <option key={task.id} value={task.id}>
                  {task.name} ({task.story_points} pts)
                </option>
              ))}
            </select>
            <button
              disabled={taskId === ""}
              onClick={() =>
                void run(async () => {
                  await addTaskToSprint(email, sprintId, Number(taskId));
                  setTaskId("");
                  onChange();
                })
              }
            >
              <Plus size={16} /> Add to sprint
            </button>
          </div>
          <ul>
            {inSprint.map((task) => (
              <li key={task.id}>
                <span className="grow">{task.name}</span>
                <span className="badge" data-status={task.status}>
                  {task.status}
                </span>
                <span>{task.story_points} pts</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
