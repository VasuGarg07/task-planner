import { type User, getLogs } from "./api";
import { useLoad } from "./useLoad";
import { userName } from "./userName";

interface Props {
  email: string;
  projectId: number;
  users: User[];
}

export default function ActivityTab({ email, projectId, users }: Props) {
  const { data, error } = useLoad(() => getLogs(email, projectId), [email, projectId]);
  const logs = data ?? [];

  return (
    <section className="card">
      <h2>Activity</h2>
      {error !== "" && <p className="error">{error}</p>}
      {data !== null && logs.length === 0 && <p className="muted">Nothing has happened yet.</p>}
      <ul>
        {logs.map((log) => (
          <li className="block" key={log.id}>
            <div>
              <strong>
                {userName(users, log.actor_id, "unknown user")} {log.action_type} {log.subject_type} #
                {log.subject_id}
              </strong>{" "}
              <span className="muted">{new Date(log.created_at).toLocaleString()}</span>
            </div>
            <details>
              <summary className="muted">Change record</summary>
              <pre>{JSON.stringify(log.change_record, null, 2)}</pre>
            </details>
          </li>
        ))}
      </ul>
    </section>
  );
}
