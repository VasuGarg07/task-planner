import { Trash2, UserPlus } from "lucide-react";
import { type FormEvent, useState } from "react";

import Avatar from "./Avatar";
import Pager from "./Pager";
import { ROLES, type Role, createUser, deleteUser, getUsers } from "./api";
import { useLoad } from "./useLoad";

interface Props {
  onChange: () => void;
}

export default function UsersPage({ onChange }: Props) {
  const [page, setPage] = useState(1);
  const [username, setUsername] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [role, setRole] = useState<Role>("BA");
  const { data, error, run } = useLoad(() => getUsers(page), [page]);
  const users = data ?? [];

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    await run(async () => {
      await createUser({ username, email: userEmail, role });
      setUsername("");
      setUserEmail("");
      onChange();
    });
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Users</h1>
          <p className="muted">People who can act in the app. Only a PM can create projects and sprints.</p>
        </div>
      </div>

      <form className="card toolbar" onSubmit={(event) => void handleCreate(event)}>
        <input placeholder="Username" value={username} onChange={(event) => setUsername(event.target.value)} />
        <input placeholder="Email" value={userEmail} onChange={(event) => setUserEmail(event.target.value)} />
        <select value={role} onChange={(event) => setRole(event.target.value as Role)}>
          {ROLES.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
        <button className="primary" type="submit">
          <UserPlus size={16} /> Add user
        </button>
      </form>

      {error !== "" && <p className="error">{error}</p>}

      <section className="card list-card">
        <ul>
          {users.map((user) => (
            <li key={user.id}>
              <Avatar name={user.username} />
              <div className="grow">
                <strong>{user.username}</strong>
                <span className="muted">{user.email}</span>
              </div>
              <span className="badge">{user.role}</span>
              <button
                className="danger icon"
                title="Delete user"
                onClick={() =>
                  void run(async () => {
                    await deleteUser(user.id);
                    onChange();
                  })
                }
              >
                <Trash2 size={16} />
              </button>
            </li>
          ))}
        </ul>
      </section>
      <Pager page={page} count={users.length} onPage={setPage} />
    </>
  );
}
