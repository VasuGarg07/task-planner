import { type FormEvent, useState } from "react";

import { ROLES, type Role, createUser, deleteUser, getUsers } from "./api";
import Pager from "./Pager";
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
    <section className="card">
      <h2>Users</h2>
      <form className="row" onSubmit={(event) => void handleCreate(event)}>
        <input placeholder="Username" value={username} onChange={(event) => setUsername(event.target.value)} />
        <input placeholder="Email" value={userEmail} onChange={(event) => setUserEmail(event.target.value)} />
        <select value={role} onChange={(event) => setRole(event.target.value as Role)}>
          {ROLES.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
        <button className="primary" type="submit">
          Add user
        </button>
      </form>
      {error !== "" && <p className="error">{error}</p>}
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            <div className="grow">
              <strong>{user.username}</strong>
              <span className="muted">{user.email}</span>
            </div>
            <span className="badge">{user.role}</span>
            <button
              onClick={() =>
                void run(async () => {
                  await deleteUser(user.id);
                  onChange();
                })
              }
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
      <Pager page={page} count={users.length} onPage={setPage} />
    </section>
  );
}
