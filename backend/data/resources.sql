CREATE TABLE IF NOT EXISTS resources (
    resource_id SERIAL PRIMARY KEY,
    skill_id INT NOT NULL,
    title VARCHAR(200),
    resource_type VARCHAR(50),
    url TEXT,
    provider VARCHAR(150),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- =========================
-- Data Science Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(1,'Python for Everybody','Course','https://www.coursera.org/specializations/python','Coursera'),
(2,'Statistics for Data Science','Course','https://www.udemy.com/course/statistics-for-data-science','Udemy'),
(3,'Data Visualization with Python','Video','https://youtube.com/datavisualization','YouTube'),
(4,'Data Cleaning in Python','Article','https://realpython.com/python-data-cleaning/','RealPython'),
(5,'SQL for Data Science','Course','https://www.coursera.org/learn/sql-for-data-science','Coursera'),
(6,'Machine Learning A-Z','Course','https://www.udemy.com/course/machinelearning/','Udemy'),
(7,'Deep Learning Specialization','Course','https://www.coursera.org/specializations/deep-learning','Coursera'),
(8,'NLP with Python','Course','https://www.coursera.org/learn/natural-language-processing','Coursera'),
(9,'Big Data Essentials','Course','https://www.coursera.org/learn/big-data-essentials','Coursera');

-- AI Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(10,'Python for AI','Course','https://www.coursera.org/specializations/python','Coursera'),
(11,'Math for Machine Learning','Course','https://www.coursera.org/learn/math-for-machine-learning','Coursera'),
(12,'Introduction to AI','Video','https://youtube.com/ai-intro','YouTube'),
(13,'ML Algorithms','Course','https://www.udemy.com/course/machinelearning','Udemy'),
(14,'Neural Networks Basics','Course','https://www.coursera.org/learn/neural-networks','Coursera'),
(15,'Data Preprocessing for AI','Article','https://www.datacamp.com/community/tutorials/data-preprocessing-python','DataCamp'),
(16,'Deep Reinforcement Learning','Course','https://www.coursera.org/learn/deep-reinforcement-learning','Coursera'),
(17,'Advanced NLP','Course','https://www.udemy.com/course/nlp-python','Udemy'),
(18,'AI Model Deployment','Article','https://mlops.community/resources/','MLOps');

-- Cybersecurity Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(19,'Networking Basics','Course','https://www.coursera.org/learn/networking-fundamentals','Coursera'),
(20,'Security Fundamentals','Course','https://www.udemy.com/course/cybersecurity-fundamentals/','Udemy'),
(21,'Ethical Hacking Introduction','Video','https://youtube.com/ethical-hacking-intro','YouTube'),
(22,'Penetration Testing','Course','https://www.udemy.com/course/penetration-testing/','Udemy'),
(23,'Network Security','Article','https://www.cisco.com/c/en/us/products/security/','Cisco'),
(24,'Cryptography Basics','Course','https://www.coursera.org/learn/crypto','Coursera'),
(25,'Forensics','Course','https://www.udemy.com/course/cyber-forensics/','Udemy'),
(26,'Advanced Security Protocols','Article','https://www.nist.gov/cyberframework','NIST'),
(27,'Threat Intelligence','Video','https://youtube.com/threat-intelligence','YouTube');

-- Web Development Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(28,'HTML & CSS','Course','https://www.coursera.org/learn/html-css','Coursera'),
(29,'JavaScript Basics','Course','https://www.udemy.com/course/javascript-basics/','Udemy'),
(30,'Responsive Design','Video','https://youtube.com/responsive-web-design','YouTube'),
(31,'React.js Crash Course','Video','https://youtube.com/reactjs','YouTube'),
(32,'Node.js & Express','Course','https://www.udemy.com/course/nodejs/','Udemy'),
(33,'RESTful APIs','Course','https://www.coursera.org/learn/restful-apis','Coursera'),
(34,'Fullstack Deployment','Video','https://youtube.com/fullstack-deployment','YouTube'),
(35,'Performance Optimization','Article','https://developers.google.com/web/fundamentals/performance','Google'),
(36,'Advanced Security','Article','https://owasp.org','OWASP');

-- Software Engineering Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(37,'Programming Foundations','Course','https://www.coursera.org/specializations/programming-fundamentals','Coursera'),
(38,'Version Control (Git)','Video','https://youtube.com/git-tutorial','YouTube'),
(39,'OOP Basics','Course','https://www.udemy.com/course/oop-in-java/','Udemy'),
(40,'DSA Fundamentals','Course','https://www.udemy.com/course/dsa/','Udemy'),
(41,'Unit Testing','Article','https://www.softwaretestinghelp.com/unit-testing-guide/','SoftwareTestingHelp'),
(42,'Design Patterns','Course','https://www.udemy.com/course/design-patterns/','Udemy'),
(43,'System Architecture','Article','https://martinfowler.com/architecture/','MartinFowler'),
(44,'CI/CD','Course','https://www.udemy.com/course/ci-cd/','Udemy'),
(45,'Agile PM','Course','https://www.coursera.org/learn/agile-project-management','Coursera');

-- Cloud Computing Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(46,'Cloud Basics','Course','https://www.coursera.org/learn/cloud-computing','Coursera'),
(47,'AWS Fundamentals','Course','https://www.aws.training','AWS'),
(48,'Virtualization Concepts','Video','https://youtube.com/virtualization','YouTube'),
(49,'Docker & Containers','Course','https://www.udemy.com/course/docker/','Udemy'),
(50,'Kubernetes Basics','Course','https://www.udemy.com/course/kubernetes/','Udemy'),
(51,'DevOps Introduction','Article','https://www.atlassian.com/devops','Atlassian'),
(52,'Cloud Architecture Design','Course','https://www.coursera.org/learn/cloud-architecture','Coursera'),
(53,'Cloud Security','Article','https://aws.amazon.com/security/','AWS'),
(54,'Serverless Computing','Video','https://youtube.com/serverless','YouTube');

-- Computer Science Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(55,'Programming Basics','Course','https://www.coursera.org/specializations/programming-fundamentals','Coursera'),
(56,'Discrete Math','Course','https://www.udemy.com/course/discrete-math/','Udemy'),
(57,'Logic & Problem Solving','Video','https://youtube.com/logic-problem-solving','YouTube'),
(58,'Data Structures','Course','https://www.udemy.com/course/data-structures/','Udemy'),
(59,'Operating Systems','Course','https://www.coursera.org/learn/operating-systems','Coursera'),
(60,'Computer Architecture','Article','https://en.wikipedia.org/wiki/Computer_architecture','Wikipedia'),
(61,'Compilers & Interpreters','Course','https://www.udemy.com/course/compiler-design/','Udemy'),
(62,'Advanced Algorithms','Course','https://www.coursera.org/learn/advanced-algorithms','Coursera'),
(63,'AI Concepts','Video','https://youtube.com/ai-concepts','YouTube');

-- Networking Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(64,'Networking Fundamentals','Course','https://www.coursera.org/learn/networking-fundamentals','Coursera'),
(65,'IP Addressing','Video','https://youtube.com/ip-addressing','YouTube'),
(66,'OSI Model','Article','https://en.wikipedia.org/wiki/OSI_model','Wikipedia'),
(67,'Routing & Switching','Course','https://www.udemy.com/course/routing-switching/','Udemy'),
(68,'Network Protocols','Article','https://en.wikipedia.org/wiki/Network_protocol','Wikipedia'),
(69,'Wireless Networking','Video','https://youtube.com/wireless-networking','YouTube'),
(70,'Network Security','Course','https://www.coursera.org/learn/network-security','Coursera'),
(71,'VPN & Firewalls','Article','https://www.cisco.com/c/en/us/products/security/','Cisco'),
(72,'Cloud Networking','Video','https://youtube.com/cloud-networking','YouTube');

-- Information Systems Resources
INSERT INTO resources (skill_id, title, resource_type, url, provider)
VALUES
(73,'IS Basics','Course','https://www.coursera.org/learn/information-systems','Coursera'),
(74,'Database Basics','Course','https://www.udemy.com/course/sql-for-information-systems/','Udemy'),
(75,'ERP Overview','Video','https://youtube.com/erp-intro','YouTube'),
(76,'Database Design & SQL','Course','https://www.udemy.com/course/sql-database-design/','Udemy'),
(77,'Business Process Management','Article','https://www.bpm.com','BPM.com'),
(78,'IS Strategy','Course','https://www.coursera.org/learn/information-systems-strategy','Coursera'),
(79,'IS Security & Compliance','Article','https://www.isaca.org/resources','ISACA'),
(80,'Advanced ERP Configuration','Video','https://youtube.com/erp-advanced','YouTube'),
(81,'Data Governance','Article','https://www.datagovernance.com','DataGovernance');
