import { type WorkloadEntry, getWorkload } from "./api";
import { useLoad } from "./useLoad";

interface Props {
  email: string;
  projectId: number;
}

export default function WorkloadTab({ email, projectId }: Props) {
  const { data, error } = useLoad(() => getWorkload(email, projectId), [email, projectId]);
  const report: Record<string, WorkloadEntry[]> = data === null ? {} : data.workload_report;
  const statuses = Object.entries(report);

  return (
    <section className="card">
      <h2>Workload by status</h2>
      {error !== "" && <p className="error">{error}</p>}
      {data !== null && statuses.length === 0 && <p className="muted">No assigned tasks yet.</p>}
      {statuses.map(([status, entries]) => (
        <div key={status}>
          <h3>{status}</h3>
          <ul>
            {entries.map((entry) => (
              <li key={entry.id}>
                <span className="grow">{entry.username}</span>
                <span>{entry.task_count} tasks</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}
