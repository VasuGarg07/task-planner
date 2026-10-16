import { Activity, ArrowLeft, Calendar, Gauge, ListChecks, Trash2, type LucideIcon } from "lucide-react";
import { Link, Navigate, NavLink, useNavigate, useParams } from "react-router";

import ActivityTab from "./ActivityTab";
import BoardTab from "./BoardTab";
import SprintsTab from "./SprintsTab";
import WorkloadTab from "./WorkloadTab";
import {
  PROJECT_STATUSES,
  type ProjectStatus,
  type User,
  deleteProject,
  getProject,
  setProjectStatus,
} from "./api";
import { useLoad } from "./useLoad";

type Tab = "board" | "sprints" | "workload" | "activity";

const TABS: { name: Tab; icon: LucideIcon }[] = [
  { name: "board", icon: ListChecks },
  { name: "sprints", icon: Calendar },
  { name: "workload", icon: Gauge },
  { name: "activity", icon: Activity },
];

interface Props {
  email: string;
  users: User[];
}

export default function ProjectDetail({ email, users }: Props) {
  const params = useParams();
  const navigate = useNavigate();
  const id = Number(params.projectId);
  const tab = TABS.find((item) => item.name === params.tab)?.name;
  const { data: project, error, run } = useLoad(() => getProject(email, id), [email, id]);

  if (tab === undefined) return <Navigate to={`/projects/${id}/board`} replace />;

  return (
    <section>
      <Link className="back" to="/projects">
        <ArrowLeft size={16} /> Back to projects
      </Link>
      {error !== "" && <p className="error">{error}</p>}

      {project !== null && (
        <>
          <div className="page-head">
            <div>
              <h1>{project.name}</h1>
              <p className="muted">{project.description}</p>
            </div>
            <div className="row">
              <select
                value={project.status}
                onChange={(event) =>
                  void run(() => setProjectStatus(email, id, event.target.value as ProjectStatus))
                }
              >
                {PROJECT_STATUSES.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
              <button
                className="danger"
                onClick={() =>
                  void run(async () => {
                    await deleteProject(email, id);
                    navigate("/projects");
                  })
                }
              >
                <Trash2 size={16} /> Delete project
              </button>
            </div>
          </div>

          <nav className="row tabs">
            {TABS.map(({ name, icon: Icon }) => (
              <NavLink key={name} to={`/projects/${id}/${name}`}>
                <Icon size={16} /> {name}
              </NavLink>
            ))}
          </nav>

          {tab === "board" && <BoardTab email={email} projectId={id} users={users} />}
          {tab === "sprints" && <SprintsTab email={email} projectId={id} />}
          {tab === "workload" && <WorkloadTab email={email} projectId={id} />}
          {tab === "activity" && <ActivityTab email={email} projectId={id} users={users} />}
        </>
      )}
    </section>
  );
}
