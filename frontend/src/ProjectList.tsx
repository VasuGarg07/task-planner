import { type FormEvent, useState } from "react";

import {
  PROJECT_STATUSES,
  type ProjectStatus,
  createProject,
  deleteProject,
  getProjects,
} from "./api";
import Pager from "./Pager";
import { useLoad } from "./useLoad";

interface Props {
  email: string;
  onOpen: (id: number) => void;
}

export default function ProjectList({ email, onOpen }: Props) {
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
    <section className="card">
      <div className="row title-row">
        <h2>Projects</h2>
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
      <form className="row" onSubmit={(event) => void handleCreate(event)}>
        <input placeholder="Project name" value={name} onChange={(event) => setName(event.target.value)} />
        <input placeholder="Description" value={description} onChange={(event) => setDescription(event.target.value)} />
        <button className="primary" type="submit">
          Create project
        </button>
      </form>
      {error !== "" && <p className="error">{error}</p>}
      {projects.length === 0 && error === "" && <p className="muted">No projects.</p>}
      <ul>
        {projects.map((project) => (
          <li key={project.id}>
            <div className="grow">
              <strong>{project.name}</strong>
              <span className="muted">{project.description}</span>
            </div>
            <span className="badge">{project.status}</span>
            <button onClick={() => onOpen(project.id)}>Open</button>
            <button onClick={() => void run(() => deleteProject(email, project.id))}>
              Delete
            </button>
          </li>
        ))}
      </ul>
      <Pager page={page} count={projects.length} onPage={setPage} />
    </section>
  );
}
