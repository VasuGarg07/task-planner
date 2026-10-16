import { Plus } from "lucide-react";
import { type FormEvent, useState } from "react";

import SprintCard from "./SprintCard";
import { createSprint, getSprintReport, getTasks } from "./api";
import { useLoad } from "./useLoad";

interface Props {
  email: string;
  projectId: number;
}

export default function SprintsTab({ email, projectId }: Props) {
  const [name, setName] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [capacity, setCapacity] = useState("");
  const sprints = useLoad(() => getSprintReport(email, projectId), [email, projectId]);
  const tasks = useLoad(() => getTasks(email, projectId), [email, projectId]);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    await sprints.run(async () => {
      await createSprint(email, {
        project_id: projectId,
        name,
        start_date: start,
        end_date: end,
        max_capacity: Number(capacity),
      });
      setName("");
    });
  }

  function refresh() {
    sprints.reload();
    tasks.reload();
  }

  return (
    <section>
      <form className="card toolbar" onSubmit={(event) => void handleCreate(event)}>
        <input placeholder="Sprint name" value={name} onChange={(event) => setName(event.target.value)} />
        <input type="date" value={start} onChange={(event) => setStart(event.target.value)} />
        <input type="date" value={end} onChange={(event) => setEnd(event.target.value)} />
        <input
          type="number"
          min="1"
          placeholder="Max points"
          value={capacity}
          onChange={(event) => setCapacity(event.target.value)}
        />
        <button className="primary" type="submit">
          <Plus size={16} /> Create sprint
        </button>
      </form>

      {sprints.error !== "" && <p className="error">{sprints.error}</p>}
      {tasks.error !== "" && <p className="error">{tasks.error}</p>}

      <ul className="card list-card">
        {(sprints.data ?? []).map((sprint) => (
          <SprintCard
            key={sprint.id}
            email={email}
            sprint={sprint}
            tasks={tasks.data ?? []}
            onChange={refresh}
          />
        ))}
      </ul>
    </section>
  );
}
