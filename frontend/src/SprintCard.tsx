import { ChevronDown, ChevronUp } from "lucide-react";
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
  const percent = Math.min(100, Math.round((sprint.current_capacity / sprint.max_capacity) * 100));

  return (
    <li className="block">
      <div className="row title-row">
        <div className="grow">
          <strong>{sprint.name}</strong>
          <span className="muted">
            {sprint.start_date} to {sprint.end_date}
          </span>
        </div>
        <span className="badge" data-status={sprint.status}>
          {sprint.status}
        </span>
        <span className="points">
          {sprint.current_capacity}/{sprint.max_capacity} pts
        </span>
        <button onClick={() => setOpen(!open)}>
          {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />} {open ? "Close" : "Manage"}
        </button>
      </div>
      <div className="progress">
        <div style={{ width: `${percent}%` }} />
      </div>
      {open && <SprintDetail email={email} sprintId={sprint.id} tasks={tasks} onChange={onChange} />}
    </li>
  );
}
