import { useState } from "react";

import SprintDetail from "./SprintDetail";
import type { SprintLoad, Task } from "./api";

interface Props {
  email: string;
  sprint: SprintLoad;
  tasks: Task[];
  onChange: () => void;
}

export default function SprintCard({ email, sprint, tasks, onChange }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <li className="block">
      <div className="row title-row">
        <div className="grow">
          <strong>{sprint.name}</strong>
          <span className="muted">
            {sprint.start_date} to {sprint.end_date}
          </span>
        </div>
        <span className="badge">{sprint.status}</span>
        <span>
          {sprint.current_capacity}/{sprint.max_capacity} pts
        </span>
        <button onClick={() => setOpen(!open)}>{open ? "Close" : "Manage"}</button>
      </div>
      {open && <SprintDetail email={email} sprintId={sprint.id} tasks={tasks} onChange={onChange} />}
    </li>
  );
}
