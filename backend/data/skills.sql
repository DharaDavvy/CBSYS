CREATE TABLE IF NOT EXISTS skills (
    skill_id SERIAL PRIMARY KEY,
    stage_id INT NOT NULL,
    skill_name VARCHAR(200) NOT NULL,
    description TEXT,
    skill_order INT NOT NULL,
    FOREIGN KEY (stage_id) REFERENCES stages(stage_id) ON DELETE CASCADE
);

-- =========================
-- Data Science
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(1,'Python Fundamentals','Learn basic Python syntax and programming concepts',1),
(1,'Statistics Basics','Understand descriptive statistics, probability, and distributions',2),
(1,'Data Visualization','Learn to create charts and plots using Python libraries',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(2,'Data Cleaning & Preprocessing','Learn how to clean and prepare data for analysis',1),
(2,'SQL for Data Analysis','Use SQL to query and analyze datasets',2),
(2,'Introduction to Machine Learning','Learn ML basics and implement simple models',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(3,'Deep Learning','Learn neural networks and deep learning concepts',1),
(3,'Natural Language Processing (NLP)','Process and analyze text data',2),
(3,'Big Data Analysis','Work with large datasets using tools like Spark/Hadoop',3);

-- =========================
-- Artificial Intelligence
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(4,'Python for AI','Python programming applied to AI',1),
(4,'Linear Algebra & Math Basics','Math foundations for AI algorithms',2),
(4,'Introduction to AI Concepts','Overview of AI applications and concepts',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(5,'Machine Learning Algorithms','Implement supervised and unsupervised ML algorithms',1),
(5,'Neural Networks Basics','Understand feedforward and backpropagation',2),
(5,'Data Preprocessing for AI','Prepare data for AI model training',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(6,'Deep Reinforcement Learning','Learn RL algorithms for complex decision making',1),
(6,'Advanced NLP Techniques','Advanced text analysis and language models',2),
(6,'AI Model Deployment','Deploy AI models to production environments',3);

-- =========================
-- Cybersecurity
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(7,'Networking Basics','Understand network types and topologies',1),
(7,'Security Fundamentals','Learn basic cybersecurity concepts',2),
(7,'Ethical Hacking Introduction','Introduction to ethical hacking principles',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(8,'Penetration Testing','Learn testing techniques to identify vulnerabilities',1),
(8,'Network Security','Protect networks against attacks',2),
(8,'Cryptography Basics','Learn encryption and secure communication',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(9,'Forensics','Investigate cyber incidents',1),
(9,'Advanced Security Protocols','Learn advanced protocols for securing networks',2),
(9,'Threat Intelligence','Analyze and respond to cybersecurity threats',3);

-- =========================
-- Web Development
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(10,'HTML & CSS Basics','Learn webpage structure and styling',1),
(10,'JavaScript Basics','Introduction to programming for the web',2),
(10,'Responsive Design','Make websites mobile-friendly',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(11,'React.js Fundamentals','Learn component-based UI development',1),
(11,'Node.js & Express','Build backend APIs',2),
(11,'RESTful APIs','Design and consume REST APIs',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(12,'Fullstack Application Deployment','Deploy web applications to servers',1),
(12,'Performance Optimization','Optimize websites for speed and scalability',2),
(12,'Advanced Security Practices','Secure web applications against threats',3);

-- =========================
-- Software Engineering
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(13,'Programming Fundamentals','Core programming skills in any language',1),
(13,'Version Control (Git)','Learn Git and GitHub workflows',2),
(13,'OOP Basics','Understand object-oriented programming principles',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(14,'Data Structures & Algorithms','Implement key data structures and algorithms',1),
(14,'Unit Testing & Debugging','Test and debug software programs',2),
(14,'Software Design Patterns','Apply common software design patterns',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(15,'System Architecture Design','Design scalable and maintainable systems',1),
(15,'Continuous Integration/Deployment (CI/CD)','Automate build and deployment pipelines',2),
(15,'Agile Project Management','Manage software projects using Agile methodology',3);

-- =========================
-- Cloud Computing
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(16,'Cloud Computing Basics','Understand cloud service models and providers',1),
(16,'AWS/Azure Fundamentals','Learn basics of major cloud platforms',2),
(16,'Virtualization Concepts','Learn virtual machines and containers',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(17,'Containers & Docker','Use Docker for containerized applications',1),
(17,'Kubernetes Basics','Orchestrate containers using Kubernetes',2),
(17,'DevOps Introduction','Learn DevOps culture and CI/CD',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(18,'Cloud Architecture Design','Design scalable cloud solutions',1),
(18,'Cloud Security Best Practices','Secure cloud infrastructure',2),
(18,'Serverless Computing','Use serverless functions for applications',3);

-- =========================
-- Computer Science
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(19,'Programming Fundamentals','Basic coding and logic',1),
(19,'Discrete Mathematics','Learn math foundations for CS',2),
(19,'Logic & Problem Solving','Solve computational problems',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(20,'Data Structures','Implement arrays, lists, trees, graphs',1),
(20,'Operating Systems','Learn OS concepts like processes and memory',2),
(20,'Computer Architecture','Study CPU, memory, and instruction cycles',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(21,'Compilers & Interpreters','Understand language translation',1),
(21,'Advanced Algorithms','Solve complex algorithmic problems',2),
(21,'Artificial Intelligence Concepts','Advanced AI theory and techniques',3);

-- =========================
-- Networking
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(22,'Network Fundamentals','Learn network basics',1),
(22,'IP Addressing & Subnetting','Understand IP addresses and subnet masks',2),
(22,'OSI Model Basics','Learn the OSI networking layers',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(23,'Routing & Switching','Configure routers and switches',1),
(23,'Network Protocols (TCP/IP)','Understand communication protocols',2),
(23,'Wireless Networking','Setup and manage Wi-Fi networks',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(24,'Network Security','Secure networks from attacks',1),
(24,'VPN & Firewalls','Implement secure network connections',2),
(24,'Cloud Networking','Integrate networks with cloud infrastructure',3);

-- =========================
-- Information Systems
-- Beginner
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(25,'IS Fundamentals','Basics of Information Systems',1),
(25,'Database Basics','Learn basic database concepts',2),
(25,'ERP Systems Overview','Introduction to ERP systems',3);

-- Intermediate
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(26,'Database Design & SQL','Design databases and use SQL',1),
(26,'Business Process Management','Understand business workflows',2),
(26,'Information Systems Strategy','Align IS with business goals',3);

-- Advanced
INSERT INTO skills (stage_id, skill_name, description, skill_order)
VALUES
(27,'IS Security & Compliance','Ensure IS meets security standards',1),
(27,'Advanced ERP Configuration','Customize ERP solutions',2),
(27,'Data Governance','Manage data policies and quality',3);
