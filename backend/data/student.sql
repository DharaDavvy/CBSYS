CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150),
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO students (full_name, email, password_hash)
VALUES 
('John Doe','john.doe@example.com','hashed_password_here'),
('Jane Smith','jane.smith@example.com','hashed_password_here');
