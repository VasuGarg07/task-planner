import { FolderKanban, Plus, Trash2 } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link } from "react-router";

import Pager from "./Pager";
import {
  PROJECT_STATUSES,
  type ProjectStatus,
  createProject,
  deleteProject,
  getProjects,
} from "./api";
import { useLoad } from "./useLoad";

interface Props {
  email: string;
}

export default function ProjectList({ email }: Props) {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<ProjectStatus | "">("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const { data, error, run } = useLoad(
    () => getProjects(email, page, status),
    [email, page, status],
  );
  const projects = data ?? [];

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    await run(async () => {
      await createProject(email, { name, description });
      setName("");
      setDescription("");
    });
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Projects</h1>
          <p className="muted">Open a project to see its board, sprints, workload and activity.</p>
        </div>
        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value as ProjectStatus | "");
            setPage(1);
          }}
        >
          <option value="">All statuses</option>
          {PROJECT_STATUSES.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
      </div>

      <form className="card toolbar" onSubmit={(event) => void handleCreate(event)}>
        <input placeholder="Project name" value={name} onChange={(event) => setName(event.target.value)} />
        <input className="wide" placeholder="Description" value={description} onChange={(event) => setDescription(event.target.value)} />
        <button className="primary" type="submit">
          <Plus size={16} /> Create project
        </button>
      </form>

      {error !== "" && <p className="error">{error}</p>}
      {projects.length === 0 && error === "" && <div className="card empty">No projects yet.</div>}

      {projects.length > 0 && (
        <section className="card list-card">
          <ul>
            {projects.map((project) => (
              <li key={project.id}>
                <span className="tile">
                  <FolderKanban size={20} />
                </span>
                <div className="grow">
                  <Link className="item-title" to={`/projects/${project.id}`}>
                    {project.name}
                  </Link>
                  <span className="muted">{project.description}</span>
                </div>
                <span className="badge" data-status={project.status}>
                  {project.status}
                </span>
                <button
                  className="danger icon"
                  title="Delete project"
                  onClick={() => void run(() => deleteProject(email, project.id))}
                >
                  <Trash2 size={16} />
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
      <Pager page={page} count={projects.length} onPage={setPage} />
    </>
  );
}
