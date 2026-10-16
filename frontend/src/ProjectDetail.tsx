import { useState } from "react";

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

const TABS: Tab[] = ["board", "sprints", "workload", "activity"];

interface Props {
  email: string;
  id: number;
  users: User[];
  onBack: () => void;
}

export default function ProjectDetail({ email, id, users, onBack }: Props) {
  const [tab, setTab] = useState<Tab>("board");
  const { data: project, error, run } = useLoad(() => getProject(email, id), [email, id]);

  return (
    <section>
      <button onClick={onBack}>Back to projects</button>
      {error !== "" && <p className="error">{error}</p>}

      {project !== null && (
        <>
          <div className="row title-row">
            <div>
              <h2>{project.name}</h2>
              <span className="muted">{project.description}</span>
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
                onClick={() =>
                  void run(async () => {
                    await deleteProject(email, id);
                    onBack();
                  })
                }
              >
                Delete project
              </button>
            </div>
          </div>

          <div className="row tabs">
            {TABS.map((name) => (
              <button key={name} className={tab === name ? "active" : ""} onClick={() => setTab(name)}>
                {name}
              </button>
            ))}
          </div>

          {tab === "board" && <BoardTab email={email} projectId={id} users={users} />}
          {tab === "sprints" && <SprintsTab email={email} projectId={id} />}
          {tab === "workload" && <WorkloadTab email={email} projectId={id} />}
          {tab === "activity" && <ActivityTab email={email} projectId={id} users={users} />}
        </>
      )}
    </section>
  );
}
