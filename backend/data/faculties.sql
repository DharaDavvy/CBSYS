CREATE TABLE IF NOT EXISTS faculties (
    faculty_id SERIAL PRIMARY KEY,
    faculty_name VARCHAR(150) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO faculties (faculty_name, description)
VALUES 
('Faculty of Computing', 'All computing related disciplines in the university');
