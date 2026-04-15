CREATE TABLE IF NOT EXISTS student_skill_progress (
    progress_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'locked', -- locked, in_progress, completed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- Example progress
INSERT INTO student_skill_progress (student_id, skill_id, status)
VALUES
(1,1,'in_progress'),
(1,2,'locked'),
(2,1,'completed'),
(2,2,'in_progress');
