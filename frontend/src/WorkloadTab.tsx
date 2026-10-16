import Avatar from "./Avatar";
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
    <>
      {error !== "" && <p className="error">{error}</p>}
      {data !== null && statuses.length === 0 && <div className="card empty">No assigned tasks yet.</div>}
      <div className="board">
        {statuses.map(([status, entries]) => (
          <section className="column" data-status={status} key={status}>
            <h3>
              <span className="badge" data-status={status}>
                {status}
              </span>
            </h3>
            <ul>
              {entries.map((entry) => (
                <li key={entry.id}>
                  <Avatar small name={entry.username} />
                  <span className="grow">{entry.username}</span>
                  <span className="points">{entry.task_count} tasks</span>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </>
  );
}
