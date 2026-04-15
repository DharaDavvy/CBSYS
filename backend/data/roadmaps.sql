CREATE TABLE IF NOT EXISTS roadmaps (
    roadmap_id SERIAL PRIMARY KEY,
    field_id INT NOT NULL,
    roadmap_title VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(field_id) ON DELETE CASCADE
);

INSERT INTO roadmaps (field_id, roadmap_title)
VALUES
(1, 'Data Science Roadmap'),
(2, 'AI Roadmap'),
(3, 'Cybersecurity Roadmap'),
(4, 'Web Development Roadmap'),
(5, 'Software Engineering Roadmap'),
(6, 'Cloud Computing Roadmap'),
(7, 'Computer Science Roadmap'),
(8, 'Networking Roadmap'),
(9, 'Information Systems Roadmap');
