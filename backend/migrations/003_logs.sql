CREATE TABLE logs (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    actor_id INT REFERENCES users(id) ON DELETE SET NULL,
    subject_type VARCHAR(10) DEFAULT 'PROJECT',
    subject_id INTEGER NOT NULL,
    action_type VARCHAR (10) DEFAULT 'CREATE',
    change_record JSONB,
    CONSTRAINT check_action_type CHECK (action_type IN ('CREATE', 'UPDATE', 'DELETE')),
    CONSTRAINT check_subject_type CHECK (subject_type IN ('PROJECT', 'SPRINT', 'TASK'))
);