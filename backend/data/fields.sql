CREATE TABLE IF NOT EXISTS fields (
    field_id SERIAL PRIMARY KEY,
    faculty_id INT NOT NULL,
    field_name VARCHAR(150) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculties(faculty_id) ON DELETE CASCADE
);

INSERT INTO fields (faculty_id, field_name)
VALUES
(1, 'Data Science'),
(1, 'Artificial Intelligence'),
(1, 'Cybersecurity'),
(1, 'Web Development'),
(1, 'Software Engineering'),
(1, 'Cloud Computing'),
(1, 'Computer Science'),
(1, 'Networking'),
(1, 'Information Systems');
