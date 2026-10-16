import Avatar from "./Avatar";
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
    <section className="card list-card">
      {error !== "" && <p className="error">{error}</p>}
      {data !== null && logs.length === 0 && <p className="muted">Nothing has happened yet.</p>}
      <ul>
        {logs.map((log) => (
          <li className="activity" key={log.id}>
            <Avatar name={userName(users, log.actor_id, "?")} />
            <div className="grow">
              <div className="row">
                <strong>{userName(users, log.actor_id, "unknown user")}</strong>
                <span className="action" data-action={log.action_type}>
                  {log.action_type}
                </span>
                <span>
                  {log.subject_type.toLowerCase()} #{log.subject_id}
                </span>
                <span className="muted">{new Date(log.created_at).toLocaleString()}</span>
              </div>
              <details>
                <summary className="muted">Change record</summary>
                <pre>{JSON.stringify(log.change_record, null, 2)}</pre>
              </details>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
