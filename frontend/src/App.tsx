import { useEffect, useState } from "react";

import { getAllUsers, getHealth } from "./api";
import ProjectDetail from "./ProjectDetail";
import ProjectList from "./ProjectList";
import UsersPage from "./UsersPage";
import { useLoad } from "./useLoad";

type View = "projects" | "users";

export default function App() {
  const [view, setView] = useState<View>("projects");
  const [projectId, setProjectId] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const loaded = useLoad(getAllUsers, []);
  const health = useLoad(getHealth, []);
  const users = loaded.data ?? [];

  useEffect(() => {
    if (loaded.data !== null && !loaded.data.some((user) => user.email === email)) {
      setEmail(loaded.data[0]?.email ?? "");
    }
  }, [loaded.data, email]);

  function show(next: View) {
    setView(next);
    setProjectId(null);
  }

  return (
    <main className="page">
      <div className="row title-row">
        <h1>Task Planner</h1>
        <div className="row">
          <span className="badge">
            {health.data === null
              ? "API unreachable"
              : `API ${health.data.status}, database ${health.data.database}`}
          </span>
          <label>
            Acting as{" "}
            <select value={email} onChange={(event) => setEmail(event.target.value)}>
              {users.map((user) => (
                <option key={user.id} value={user.email}>
                  {user.username} ({user.role})
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="row tabs">
        <button className={view === "projects" ? "active" : ""} onClick={() => show("projects")}>
          Projects
        </button>
        <button className={view === "users" ? "active" : ""} onClick={() => show("users")}>
          Users
        </button>
      </div>

      {loaded.error !== "" && <p className="error">{loaded.error}</p>}

      {view === "users" && <UsersPage onChange={loaded.reload} />}

      {view === "projects" && email === "" && (
        <p className="muted">Create a user first (Users tab), then pick it above.</p>
      )}
      {view === "projects" && email !== "" && projectId === null && (
        <ProjectList email={email} onOpen={setProjectId} />
      )}
      {view === "projects" && email !== "" && projectId !== null && (
        <ProjectDetail
          email={email}
          id={projectId}
          users={users}
          onBack={() => setProjectId(null)}
        />
      )}
    </main>
  );
}
