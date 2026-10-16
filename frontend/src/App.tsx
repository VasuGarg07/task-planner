import { Activity, FolderKanban, ListChecks, Users as UsersIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { Navigate, NavLink, Route, Routes } from "react-router";

import Avatar from "./Avatar";
import ProjectDetail from "./ProjectDetail";
import ProjectList from "./ProjectList";
import UsersPage from "./UsersPage";
import { getAllUsers, getHealth } from "./api";
import { useLoad } from "./useLoad";

export default function App() {
  const [email, setEmail] = useState("");
  const loaded = useLoad(getAllUsers, []);
  const health = useLoad(getHealth, []);
  const users = loaded.data ?? [];
  const current = users.find((user) => user.email === email);

  useEffect(() => {
    if (loaded.data !== null && !loaded.data.some((user) => user.email === email)) {
      setEmail(loaded.data[0]?.email ?? "");
    }
  }, [loaded.data, email]);

  const needUser = (
    <div className="card empty">Create a user on the Users page, then pick it in the sidebar.</div>
  );

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <ListChecks size={26} /> Task Planner
        </div>

        <nav className="nav">
          <NavLink to="/projects">
            <FolderKanban size={18} /> Projects
          </NavLink>
          <NavLink to="/users">
            <UsersIcon size={18} /> Users
          </NavLink>
        </nav>

        <div className="sidebar-foot">
          <label className="acting">
            <span className="muted">Acting as</span>
            <span className="row">
              <Avatar name={current === undefined ? "?" : current.username} />
              <select value={email} onChange={(event) => setEmail(event.target.value)}>
                {users.map((user) => (
                  <option key={user.id} value={user.email}>
                    {user.username} ({user.role})
                  </option>
                ))}
              </select>
            </span>
          </label>
          <span className="badge" data-status={health.data === null ? "DROPPED" : "DONE"}>
            <Activity size={14} />
            {health.data === null
              ? "API unreachable"
              : `API ${health.data.status}, database ${health.data.database}`}
          </span>
        </div>
      </aside>

      <main className="content">
        {loaded.error !== "" && <p className="error">{loaded.error}</p>}
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/users" element={<UsersPage onChange={loaded.reload} />} />
          <Route
            path="/projects"
            element={email === "" ? needUser : <ProjectList email={email} />}
          />
          <Route
            path="/projects/:projectId/:tab?"
            element={email === "" ? needUser : <ProjectDetail email={email} users={users} />}
          />
          <Route path="*" element={<div className="card empty">Page not found.</div>} />
        </Routes>
      </main>
    </div>
  );
}
