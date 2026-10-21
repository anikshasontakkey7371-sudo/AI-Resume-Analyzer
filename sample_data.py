"""
Sample resumes and job descriptions for rapid testing and demonstrations.
"""

SAMPLE_RESUMES = {
    "software_engineer": {
        "title": "Full Stack Software Engineer Resume",
        "text": """Alex Morgan
alex.morgan@email.com | (555) 234-5678 | San Francisco, CA
linkedin.com/in/alexmorgan-dev | github.com/alexmorgan

PROFESSIONAL SUMMARY
Results-driven Full Stack Software Engineer with 3+ years of experience designing and developing scalable web applications. Proficient in Python, JavaScript, TypeScript, React, and PostgreSQL. Experienced in microservice architectures, cloud deployments, and agile methodologies.

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3, Bash
- Frameworks & Libraries: React, Node.js, Express, Django, FastAPI, TailwindCSS, Redux
- Databases & Caching: PostgreSQL, MongoDB, Redis, SQLite
- Cloud & DevOps: AWS (EC2, S3), Docker, Git, GitHub Actions, CI/CD, Linux
- Core Competencies: RESTful APIs, System Design, Unit Testing, Agile/Scrum

PROFESSIONAL EXPERIENCE
Senior Full Stack Developer | NexaTech Solutions | June 2023 - Present
- Architected and deployed microservices backend using Python and FastAPI, serving 120,000+ daily active users with 99.98% uptime.
- Engineered responsive React and TypeScript frontend, boosting user retention by 28% and reducing initial page load time by 42%.
- Streamlined database queries and implemented Redis caching, reducing average response latency by 35%.
- Spearheaded migration from legacy monolithic architecture to Docker containerized services on AWS.

Software Engineer | CloudScale Systems | Jan 2022 - May 2023
- Developed RESTful API endpoints using Node.js, Express, and PostgreSQL handling over 2M requests weekly.
- Built interactive dashboard features in React.js with automated state management using Redux.
- Implemented comprehensive automated test suites using Jest and Pytest, boosting code coverage from 55% to 88%.
- Collaborated across 4 cross-functional teams using Agile sprints and Git workflow.

KEY PROJECTS
Real-Time Collab Canvas (React, Node.js, WebSockets, Redis)
- Developed collaborative canvas tool with real-time cursor sync and state reconciliation for up to 50 concurrent editors.
- Automated CI/CD pipeline using GitHub Actions, reducing deployment time by 60%.

E-Commerce Analytics Engine (Python, FastAPI, PostgreSQL, Docker)
- Designed an inventory forecasting microservice processing 50,000 transactions daily.
- Implemented JWT authentication and role-based access control (RBAC).

EDUCATION
B.S. in Computer Science | University of California, Berkeley | 2018 - 2022
- Relevant Coursework: Data Structures, Algorithms, Operating Systems, Database Systems, Cloud Computing.
"""
    },
    "data_scientist": {
        "title": "Data Scientist & ML Engineer Resume",
        "text": """Samantha Chen
samantha.chen@email.com | (555) 876-5432 | New York, NY
linkedin.com/in/samanthachen-ds | github.com/schen-ai

PROFESSIONAL SUMMARY
Analytical and detail-oriented Data Scientist with expertise in Machine Learning, Statistical Modeling, and Python. Proven track record of developing end-to-end predictive models, extracting actionable business intelligence, and deploying ML pipelines into production.

TECHNICAL SKILLS
- Programming Languages: Python, SQL, R, Bash
- Machine Learning & AI: PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, NLP, Computer Vision
- Databases & Cloud: PostgreSQL, Snowflake, AWS S3, Google Cloud Platform (GCP), Docker
- Visualization & BI: Tableau, PowerBI, Matplotlib, Seaborn, Plotly
- Methods: Hypothesis Testing, A/B Testing, Regression, Classification, Clustering, Deep Learning

PROFESSIONAL EXPERIENCE
Data Scientist | Apex Financial Analytics | August 2023 - Present
- Engineered gradient-boosted classification models predicting customer churn with 89% accuracy, saving an estimated $1.2M annually.
- Built automated ETL data pipelines using Python and SQL processing 10M+ daily records from Snowflake.
- Designed and analyzed 15+ A/B experiments driving a 14% improvement in digital marketing conversion rates.
- Deployed real-time inference microservice with FastAPI and Docker on AWS.

Junior Machine Learning Engineer | DataCore Labs | Jan 2022 - July 2023
- Built NLP sentiment analysis models using Transformers and Scikit-Learn to categorize 500,000 customer reviews.
- Optimized feature engineering pipelines, slashing training computation time by 30%.
- Created interactive dashboards in Tableau and Plotly for executive leadership stakeholders.

EDUCATION
M.S. in Data Science | Columbia University | 2022
B.S. in Applied Mathematics | University of Michigan | 2020
"""
    }
}

SAMPLE_JOB_DESCRIPTIONS = {
    "software_engineer": {
        "title": "Senior Full Stack Engineer",
        "text": """Job Title: Senior Full Stack Engineer
Location: Remote / Hybrid (San Francisco, CA)
Company: Elevate Software Inc.

About the Role:
We are looking for a skilled Senior Full Stack Engineer to build and scale our next-generation cloud collaboration platform. You will work closely with product managers and designers to develop elegant, robust, and scalable solutions.

Key Responsibilities:
- Design, build, and maintain efficient, reusable, and reliable code in Python and JavaScript/TypeScript.
- Develop responsive web applications using React.js and modern state management.
- Architect high-performance RESTful APIs and microservices using FastAPI, Django, or Node.js.
- Optimize database schemas and queries using PostgreSQL and Redis.
- Collaborate with DevOps engineers to containerize applications with Docker and deploy to AWS.
- Participate in code reviews, mentor junior engineers, and drive best practices in automated testing (CI/CD, Pytest, Jest).

Required Qualifications:
- 3+ years of professional full-stack software engineering experience.
- Strong proficiency in Python, JavaScript, and TypeScript.
- Deep hands-on experience with modern frontend frameworks (React, Next.js).
- Proven experience with relational databases (PostgreSQL) and caching layers (Redis).
- Familiarity with Docker, Kubernetes, and AWS cloud infrastructure.
- Experience building and maintaining CI/CD pipelines.
- Solid understanding of system design, data structures, and algorithms.
- Strong communication, problem-solving, and team collaboration skills.

Preferred Qualifications:
- Experience with GraphQL and WebSockets.
- Contributions to open-source software projects.
- Familiarity with Kubernetes and Terraform.
"""
    },
    "data_scientist": {
        "title": "Machine Learning Engineer / Data Scientist",
        "text": """Job Title: Machine Learning Engineer / Data Scientist
Location: New York, NY (Hybrid)
Company: Quantum Intelligence Corp.

About the Role:
We are seeking a talented Data Scientist / ML Engineer to lead the development of our predictive machine learning solutions. You will transform complex data into intelligent algorithms that power real-time business decisions.

Key Responsibilities:
- Build, train, evaluate, and deploy production-grade machine learning models using Python, PyTorch, and Scikit-Learn.
- Design automated ETL data pipelines in SQL and Python on Snowflake or PostgreSQL.
- Perform statistical analysis, hypothesis testing, and rigorous A/B test experiments.
- Deploy real-time and batch ML models using FastAPI, Docker, and AWS or GCP.
- Collaborate with engineering and product teams to translate business requirements into technical solutions.

Requirements:
- Bachelor's or Master's degree in Computer Science, Data Science, Statistics, or related technical field.
- 2+ years of experience developing machine learning models in Python.
- Strong expertise with Pandas, NumPy, Scikit-Learn, PyTorch, or TensorFlow.
- Advanced SQL querying skills and experience with relational/cloud data warehouses.
- Hands-on experience with containerization (Docker) and cloud services (AWS or GCP).
- Strong communication skills to present findings to non-technical stakeholders.
"""
    }
}
