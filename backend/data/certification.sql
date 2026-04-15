CREATE TABLE certifications (
    certification_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    roadmap_id INT NOT NULL,
    certificate_name VARCHAR(200),
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id)
);
