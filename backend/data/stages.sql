CREATE TABLE IF NOT EXISTS stages (
    stage_id SERIAL PRIMARY KEY,
    roadmap_id INT NOT NULL,
    stage_name VARCHAR(50) NOT NULL,
    stage_order INT NOT NULL,
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE
);

-- Add Beginner, Intermediate, Advanced for all fields
INSERT INTO stages (roadmap_id, stage_name, stage_order)
VALUES
-- Data Science
(1,'Beginner',1),(1,'Intermediate',2),(1,'Advanced',3),
-- AI
(2,'Beginner',1),(2,'Intermediate',2),(2,'Advanced',3),
-- Cybersecurity
(3,'Beginner',1),(3,'Intermediate',2),(3,'Advanced',3),
-- Web Development
(4,'Beginner',1),(4,'Intermediate',2),(4,'Advanced',3),
-- Software Engineering
(5,'Beginner',1),(5,'Intermediate',2),(5,'Advanced',3),
-- Cloud Computing
(6,'Beginner',1),(6,'Intermediate',2),(6,'Advanced',3),
-- Computer Science
(7,'Beginner',1),(7,'Intermediate',2),(7,'Advanced',3),
-- Networking
(8,'Beginner',1),(8,'Intermediate',2),(8,'Advanced',3),
-- Information Systems
(9,'Beginner',1),(9,'Intermediate',2),(9,'Advanced',3);
