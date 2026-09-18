import json
from datetime import datetime, timedelta
from models import (
    db, User, StudentProfile, StudentProject, StudentCertification,
    StudentAchievement, StudentExperience, IndustryProfile, AcademicianProfile,
    InstitutionProfile, Skill, StudentSkill, CareerRequirement, Assessment,
    AssessmentQuestion, Opportunity, LearningResource, Collaboration, Notification
)
from auth import hash_password

def seed_database(app=None, reset=True):
    if app is None:
        from app import create_app
        app = create_app()
    with app.app_context():
        # Reset is used by the explicit seed command; startup only fills an empty database.
        if reset:
            db.drop_all()
        db.create_all()
        if not reset and User.query.first():
            return
        print("Initialized database schema.")

        # -------------------------------------------------------------
        # 1. SEED USERS & PROFILES
        # -------------------------------------------------------------
        # Student Demo Account
        student_user = User(
            email='student@demo.skillbridge.local',
            password_hash=hash_password('Demo@123'),
            role='student'
        )
        db.session.add(student_user)
        db.session.flush()

        student_profile = StudentProfile(
            user_id=student_user.id,
            name_display='Student 123',
            college='Demo University',
            branch='Computer Science',
            year='2nd Year',
            cgpa=3.8,
            bio='Passionate about learning, problem solving, and building scalable full-stack applications.',
            career_goal='Software Developer',
            resume_file_path='resumes/demo_student_resume.pdf',
            github_url='https://github.com/student123-demo',
            linkedin_url='https://linkedin.com/in/student123-demo',
            portfolio_url='https://student123.dev'
        )
        student_profile.interested_domains = ['Web Development', 'AI/ML', 'Cloud Computing']
        db.session.add(student_profile)
        db.session.flush()

        # Seed Student Projects
        p1 = StudentProject(
            student_id=student_profile.id,
            title='Campus Resource Sharing Portal',
            description='A microservices web platform for students to swap academic materials and textbook summaries with real-time updates.',
            technologies='Python, Flask, SQLite, Bootstrap',
            start_date='2023-09-01',
            end_date='2023-12-15',
            role='Lead Developer',
            project_url='https://github.com/student123-demo/campus-share'
        )
        p2 = StudentProject(
            student_id=student_profile.id,
            title='Smart Task Prioritizer',
            description='A priority queue algorithm visualizer and task scheduler implementing A* pathfinding and Dijkstra algorithms.',
            technologies='C++, Data Structures, Algorithms',
            start_date='2024-01-10',
            end_date='2024-03-20',
            role='Sole Author',
            project_url='https://github.com/student123-demo/task-prioritizer'
        )
        db.session.add_all([p1, p2])

        # Seed Student Certifications
        c1 = StudentCertification(
            student_id=student_profile.id,
            name='AWS Certified Cloud Practitioner',
            issuing_org='Amazon Web Services',
            issue_date='2023-11-12',
            credential_url='https://aws.amazon.com/verification'
        )
        db.session.add(c1)

        # Seed Student Achievements
        a1 = StudentAchievement(
            student_id=student_profile.id,
            title='Top 10 Finalist in HackSouth Tech Hackathon',
            description='Built an offline-first emergency coordination portal for student campus volunteers.',
            date_achieved='2023-10-28'
        )
        db.session.add(a1)

        # Seed Student Experience
        e1 = StudentExperience(
            student_id=student_profile.id,
            company='InnoTech Labs',
            role='Software Engineering Intern',
            duration='2 months (May - July 2023)',
            description='Developed REST APIs and database schema migrations; reduced API response latency by 18%.',
            skills_used='Python, SQL, Git, RESTful Architecture'
        )
        db.session.add(e1)

        # Industry Demo Account
        industry_user = User(
            email='industry@demo.skillbridge.local',
            password_hash=hash_password('Demo@123'),
            role='industry'
        )
        db.session.add(industry_user)
        db.session.flush()

        industry_profile = IndustryProfile(
            user_id=industry_user.id,
            company_name='Demo Tech Solutions',
            industry='Technology & Software',
            company_size='250-1000',
            location='Hyderabad, India',
            website='https://demotech.example.com',
            description='Demo Tech Solutions is an enterprise engineering and cloud computing software house.'
        )
        industry_profile.hiring_interests = ['Internships', 'Full-time', 'Apprenticeships']
        industry_profile.commonly_required_skills = ['Python', 'Data Structures', 'SQL', 'Git/GitHub', 'Web Development']
        industry_profile.collaboration_interests = ['Guest Lectures', 'Workshops', 'Live Projects', 'Research Collaborations']
        db.session.add(industry_profile)
        db.session.flush()

        # Academician Demo Account
        academician_user = User(
            email='academician@demo.skillbridge.local',
            password_hash=hash_password('Demo@123'),
            role='academician'
        )
        db.session.add(academician_user)
        db.session.flush()

        academician_profile = AcademicianProfile(
            user_id=academician_user.id,
            name_display='Dr. A. Sharma',
            institution='Demo University',
            department='Computer Science & Engineering',
            designation='Assistant Professor',
            experience_years=7,
            linkedin_url='https://linkedin.com/in/faculty-demo',
            website_url='https://faculty.demouniversity.edu/asharma'
        )
        academician_profile.expertise_areas = ['Machine Learning', 'Data Structures', 'Cloud Architecture', 'Curriculum Design']
        academician_profile.research_interests = ['Applied AI in Education', 'Distributed Systems Optimization']
        db.session.add(academician_profile)
        db.session.flush()

        # Institution Demo Account
        institution_user = User(
            email='institution@demo.skillbridge.local',
            password_hash=hash_password('Demo@123'),
            role='institution'
        )
        db.session.add(institution_user)
        db.session.flush()

        institution_profile = InstitutionProfile(
            name='Demo University',
            admin_user_id=institution_user.id,
            location='Hyderabad, India',
            description='Autonomous university focused on industry-aligned technical education and experiential learning.'
        )
        db.session.add(institution_profile)
        db.session.flush()

        # -------------------------------------------------------------
        # 2. SEED SKILLS
        # -------------------------------------------------------------
        skills_data = [
            # Technical
            ('C Programming', 'technical'),
            ('Python', 'technical'),
            ('Java', 'technical'),
            ('JavaScript', 'technical'),
            ('SQL', 'technical'),
            ('Data Structures', 'technical'),
            ('Algorithms', 'technical'),
            ('Web Development', 'technical'),
            ('Git/GitHub', 'technical'),
            ('Machine Learning', 'technical'),
            ('Statistics', 'technical'),
            ('Cloud Computing', 'technical'),
            # Soft
            ('Communication', 'soft'),
            ('Problem Solving', 'soft'),
            ('Teamwork', 'soft'),
            ('Leadership', 'soft'),
            ('Time Management', 'soft'),
            ('Adaptability', 'soft')
        ]

        skills_dict = {}
        for name, cat in skills_data:
            s = Skill(name=name, category=cat)
            db.session.add(s)
            skills_dict[name] = s
        db.session.flush()

        # -------------------------------------------------------------
        # 3. SEED STUDENT 123 SKILLS (Realistic prompt requirements)
        # -------------------------------------------------------------
        # Technical:
        # C Programming: 65/100 (verified)
        # Python: Not Assessed
        # Data Structures: 72/100 (verified)
        # SQL: Not Assessed
        # Web Development: Not Assessed
        # Git/GitHub: 58/100 (verified)
        # Java: Not Assessed
        # Soft:
        # Communication: 75/100 (verified)
        # Problem Solving: Not Assessed
        # Teamwork: 70/100 (verified)
        student_skills_seed = [
            ('C Programming', 65, True),
            ('Python', None, False),
            ('Data Structures', 72, True),
            ('SQL', None, False),
            ('Web Development', None, False),
            ('Git/GitHub', 58, True),
            ('Java', None, False),
            ('Communication', 75, True),
            ('Problem Solving', None, False),
            ('Teamwork', 70, True)
        ]

        for sname, vscore, is_v in student_skills_seed:
            sk = skills_dict.get(sname)
            if sk:
                ss = StudentSkill(
                    student_id=student_profile.id,
                    skill_id=sk.id,
                    verified_score=vscore,
                    self_rated_score=vscore if vscore else 60,
                    is_verified=is_v,
                    verified_date=datetime.utcnow() - timedelta(days=10) if is_v else None
                )
                db.session.add(ss)

        # -------------------------------------------------------------
        # 4. SEED CAREER REQUIREMENTS
        # -------------------------------------------------------------
        career_reqs = [
            {
                'career_goal': 'Software Developer',
                'required_skills': ['C Programming', 'Data Structures', 'Problem Solving', 'Communication', 'Algorithms'],
                'minimum_scores': [70, 75, 70, 60, 70]
            },
            {
                'career_goal': 'Data Scientist',
                'required_skills': ['Python', 'Statistics', 'Data Structures', 'Problem Solving', 'Communication'],
                'minimum_scores': [80, 75, 70, 75, 60]
            },
            {
                'career_goal': 'Web Developer',
                'required_skills': ['Web Development', 'JavaScript', 'SQL', 'Problem Solving', 'Communication'],
                'minimum_scores': [75, 70, 65, 70, 65]
            },
            {
                'career_goal': 'AI/ML Engineer',
                'required_skills': ['Python', 'Machine Learning', 'Statistics', 'Problem Solving', 'Data Structures'],
                'minimum_scores': [80, 75, 75, 75, 70]
            },
            {
                'career_goal': 'Cloud Engineer',
                'required_skills': ['Cloud Computing', 'Python', 'Git/GitHub', 'Problem Solving', 'Communication'],
                'minimum_scores': [75, 70, 65, 70, 65]
            },
            {
                'career_goal': 'Data Analyst',
                'required_skills': ['SQL', 'Python', 'Statistics', 'Problem Solving', 'Communication'],
                'minimum_scores': [75, 70, 70, 70, 65]
            },
            {
                'career_goal': 'Mobile App Developer',
                'required_skills': ['Java', 'Data Structures', 'Problem Solving', 'Git/GitHub', 'Communication'],
                'minimum_scores': [75, 70, 70, 65, 60]
            },
            {
                'career_goal': 'DevOps Engineer',
                'required_skills': ['Git/GitHub', 'Cloud Computing', 'Python', 'Problem Solving', 'Communication'],
                'minimum_scores': [75, 75, 70, 70, 65]
            }
        ]

        for cr in career_reqs:
            req_obj = CareerRequirement(
                career_goal=cr['career_goal']
            )
            req_obj.required_skills = cr['required_skills']
            req_obj.minimum_scores = cr['minimum_scores']
            db.session.add(req_obj)

        # -------------------------------------------------------------
        # 5. SEED ASSESSMENTS & QUESTIONS
        # -------------------------------------------------------------
        # Python Assessment
        python_skill = skills_dict['Python']
        py_assess = Assessment(
            skill_id=python_skill.id,
            difficulty='medium',
            title='Python Fundamentals Assessment',
            instructions='Answer 8 core questions covering Python syntax, data types, scoping, and built-in functions. 20-minute limit.',
            time_limit_mins=20
        )
        db.session.add(py_assess)
        db.session.flush()

        py_questions = [
            (
                "What is the output of `bool([])` in Python?",
                ["True", "False", "None", "Error"],
                1,
                "In Python, empty sequences such as empty lists [] evaluate to False in boolean contexts.",
                "Data Types"
            ),
            (
                "Which keyword is used to define an anonymous function in Python?",
                ["def", "lambda", "func", "anonymous"],
                1,
                "The `lambda` keyword defines anonymous, inline functions in Python.",
                "Functions"
            ),
            (
                "What is the time complexity of looking up a key in a standard Python dictionary on average?",
                ["O(n)", "O(1)", "O(log n)", "O(n^2)"],
                1,
                "Python dictionaries are implemented as hash tables, giving average O(1) key lookups.",
                "Data Structures"
            ),
            (
                "What will `print(type((1,)))` display?",
                ["<class 'int'>", "<class 'tuple'>", "<class 'list'>", "<class 'set'>"],
                1,
                "A comma after an element inside parentheses creates a single-element tuple.",
                "Syntax"
            ),
            (
                "Which method is called automatically when an object is instantiated in a Python class?",
                ["__new__", "__init__", "__start__", "__main__"],
                1,
                "__init__ is the initializer method called after instance creation to set initial state.",
                "OOP"
            ),
            (
                "How do you open a file for reading in a context manager to ensure safe closing?",
                ["file = open('data.txt')", "with open('data.txt', 'r') as f:", "open('data.txt').read()", "using open('data.txt')"],
                1,
                "The `with` statement creates a context manager that safely closes file streams even on errors.",
                "File I/O"
            ),
            (
                "What is the result of `'Hello' + 3` in Python 3?",
                ["Hello3", "TypeError", "SyntaxError", "ValueError"],
                1,
                "Python does not perform implicit string concatenation with integers; it raises a TypeError.",
                "Data Types"
            ),
            (
                "What does the `pass` statement do in Python?",
                ["Breaks a loop", "Skips next iteration", "Acts as a null operation placeholder", "Returns None immediately"],
                2,
                "`pass` is a syntactic placeholder that does nothing when executed.",
                "Syntax"
            ),
            (
                "What built-in module provides tools for working with iterators and generator combinations?",
                ["collections", "itertools", "functools", "sys"],
                1,
                "`itertools` implements memory-efficient iterator building blocks.",
                "Standard Library"
            )
        ]

        for q_text, opts, correct_idx, expl, topic in py_questions:
            q = AssessmentQuestion(
                assessment_id=py_assess.id,
                question_text=q_text,
                correct_option_index=correct_idx,
                explanation=expl,
                topic=topic,
                difficulty='medium'
            )
            q.options = opts
            db.session.add(q)

        # Data Structures Assessment
        dsa_skill = skills_dict['Data Structures']
        dsa_assess = Assessment(
            skill_id=dsa_skill.id,
            difficulty='medium',
            title='Data Structures & Arrays Assessment',
            instructions='Answer questions on lists, stacks, queues, trees, and hashing efficiency.',
            time_limit_mins=25
        )
        db.session.add(dsa_assess)
        db.session.flush()

        dsa_questions = [
            (
                "Which data structure operates on a Last-In, First-Out (LIFO) principle?",
                ["Queue", "Stack", "Binary Heap", "Linked List"],
                1,
                "A stack is a LIFO data structure where elements are pushed and popped from the top.",
                "Linear Structures"
            ),
            (
                "What is the worst-case search time complexity in a balanced Binary Search Tree (AVL)?",
                ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
                1,
                "Self-balancing BSTs like AVL trees maintain logarithmic height, guaranteeing O(log n) search.",
                "Trees"
            ),
            (
                "Which data structure is typically used for Breadth-First Search (BFS) graph traversal?",
                ["Stack", "Queue", "Priority Queue", "Hash Map"],
                1,
                "A queue provides FIFO ordering necessary for level-by-level breadth exploration.",
                "Graphs"
            ),
            (
                "What is the primary advantage of a doubly-linked list over a singly-linked list?",
                ["Less memory usage", "Bidirectional traversal and fast deletion with node pointer", "O(1) random indexing", "Cache locality"],
                1,
                "Doubly linked lists have prev pointers allowing reverse traversal and O(1) removal given a node pointer.",
                "Linked Lists"
            ),
            (
                "In open-addressing hash tables, what is linear probing used for?",
                ["Dynamic resizing", "Collision resolution", "Sorting keys", "Garbage collection"],
                1,
                "Linear probing sequentially checks adjacent slots when a hash collision occurs.",
                "Hashing"
            ),
            (
                "What is the space complexity of an adjacency matrix representation of a graph with V vertices?",
                ["O(V)", "O(V^2)", "O(V + E)", "O(E)"],
                1,
                "An adjacency matrix allocates a V x V grid, consuming O(V^2) memory regardless of edge density.",
                "Graphs"
            ),
            (
                "Which heap property must be satisfied in a Min-Heap?",
                ["Parent is smaller than or equal to its children", "Parent is greater than its children", "All leaves are sorted", "Left child < Right child"],
                0,
                "In a Min-Heap, every parent node has a key less than or equal to its child nodes.",
                "Heaps"
            ),
            (
                "What is the amortized cost of inserting an element into a dynamic array (vector)?",
                ["O(n)", "O(1)", "O(log n)", "O(n^2)"],
                1,
                "While individual resizing takes O(n), amortized over a series of insertions the cost is O(1).",
                "Arrays"
            )
        ]

        for q_text, opts, correct_idx, expl, topic in dsa_questions:
            q = AssessmentQuestion(
                assessment_id=dsa_assess.id,
                question_text=q_text,
                correct_option_index=correct_idx,
                explanation=expl,
                topic=topic,
                difficulty='medium'
            )
            q.options = opts
            db.session.add(q)

        # SQL Assessment
        sql_skill = skills_dict['SQL']
        sql_assess = Assessment(
            skill_id=sql_skill.id,
            difficulty='medium',
            title='Relational Databases & SQL Assessment',
            instructions='Test your knowledge of JOINs, aggregation, indexing, and transactional isolation.',
            time_limit_mins=20
        )
        db.session.add(sql_assess)
        db.session.flush()

        sql_questions = [
            (
                "Which SQL JOIN returns only matching records from both tables?",
                ["LEFT JOIN", "INNER JOIN", "FULL OUTER JOIN", "CROSS JOIN"],
                1,
                "INNER JOIN matches rows that have corresponding values in both tables.",
                "Joins"
            ),
            (
                "Which clause is used to filter groups created by the GROUP BY clause?",
                ["WHERE", "HAVING", "FILTER", "LIMIT"],
                1,
                "HAVING filters aggregated grouped results, while WHERE filters individual rows before grouping.",
                "Aggregation"
            ),
            (
                "What does ACID stand for in database transactions?",
                ["Atomicity, Consistency, Isolation, Durability", "Accuracy, Concurrency, Integrity, Distribution", "Action, Commit, Index, Data", "Access, Control, Identification, Delegation"],
                0,
                "ACID guarantees transactional safety: Atomicity, Consistency, Isolation, Durability.",
                "Transactions"
            ),
            (
                "Which SQL constraint ensures all values in a column are distinct and cannot be null?",
                ["UNIQUE", "PRIMARY KEY", "FOREIGN KEY", "CHECK"],
                1,
                "A PRIMARY KEY uniquely identifies each row and strictly prohibits NULL values.",
                "Schema"
            ),
            (
                "What is the difference between TRUNCATE and DELETE in SQL?",
                ["TRUNCATE is DDL and faster without logging each row; DELETE is DML and can have a WHERE clause", "DELETE resets identity counters while TRUNCATE does not", "TRUNCATE is reversible with rollback in all engines without logging", "There is no difference"],
                0,
                "TRUNCATE deallocates pages directly (DDL), whereas DELETE removes rows individually and logs operations (DML).",
                "Data Manipulation"
            ),
            (
                "How do you eliminate duplicate rows from a query result set?",
                ["UNIQUE", "DISTINCT", "DIFFERENT", "ISOLATE"],
                1,
                "SELECT DISTINCT filters out identical rows from query output.",
                "Querying"
            ),
            (
                "Which index structure is the default in most relational database engines (PostgreSQL, MySQL InnoDB)?",
                ["Hash index", "B-Tree index", "R-Tree index", "Bitmap index"],
                1,
                "B-Tree indexes support both equality and range searches with balanced logarithmic lookup times.",
                "Indexing"
            ),
            (
                "What will `COUNT(*)` return if a table contains 5 rows with NULL values in some columns?",
                ["0", "5", "Null", "Error"],
                1,
                "COUNT(*) counts all rows in the result set regardless of NULL values in individual columns.",
                "Aggregation"
            )
        ]

        for q_text, opts, correct_idx, expl, topic in sql_questions:
            q = AssessmentQuestion(
                assessment_id=sql_assess.id,
                question_text=q_text,
                correct_option_index=correct_idx,
                explanation=expl,
                topic=topic,
                difficulty='medium'
            )
            q.options = opts
            db.session.add(q)

        # -------------------------------------------------------------
        # 6. SEED REAL-WORLD LEARNING RESOURCES
        # -------------------------------------------------------------
        resources_seed = [
            {
                'title': 'CS50: Introduction to Computer Science',
                'provider': 'Harvard University (edX / YouTube)',
                'category': 'Programming Languages',
                'skill': 'C Programming',
                'difficulty': 'Beginner',
                'external_url': 'https://www.youtube.com/watch?v=8mAITcNt710',
                'description': 'Harvard University open course covering algorithmic thinking, C memory management, pointers, and memory layout.',
                'is_free': True,
                'resource_type': 'Course',
                'duration': '12 weeks (Self-paced)',
                'why_recommended': 'Foundational prerequisite for Software Developer career goal.'
            },
            {
                'title': 'Python Full Course for Beginners',
                'provider': 'freeCodeCamp',
                'category': 'Programming Languages',
                'skill': 'Python',
                'difficulty': 'Beginner',
                'external_url': 'https://www.youtube.com/watch?v=rfscVS0vtbw',
                'description': 'Comprehensive 4+ hour tutorial covering variables, loops, dictionary data structures, object-oriented concepts, and modules.',
                'is_free': True,
                'resource_type': 'Video',
                'duration': '4.5 hours',
                'why_recommended': 'High skill gap in Python for your Software Developer goal.'
            },
            {
                'title': 'The Official Python 3 Documentation & Tutorial',
                'provider': 'Python Software Foundation',
                'category': 'Programming Languages',
                'skill': 'Python',
                'difficulty': 'Intermediate',
                'external_url': 'https://docs.python.org/3/tutorial/',
                'description': 'Official guide to Python syntax, standard library, decorators, generators, and exception handling best practices.',
                'is_free': True,
                'resource_type': 'Documentation',
                'duration': '6 hours',
                'why_recommended': 'Master standard library conventions and memory models.'
            },
            {
                'title': 'Data Structures and Algorithms in Python',
                'provider': 'freeCodeCamp',
                'category': 'Data Structures',
                'skill': 'Data Structures',
                'difficulty': 'Intermediate',
                'external_url': 'https://www.youtube.com/watch?v=pkYVOmU3MgA',
                'description': 'Deep dive into binary search, dynamic arrays, linked lists, trees, graphs, dynamic programming, and complexity analysis.',
                'is_free': True,
                'resource_type': 'Course',
                'duration': '13 hours',
                'why_recommended': 'DSA is a high-priority gap for your Software Developer goal.'
            },
            {
                'title': 'SQL for Data Science and Engineering',
                'provider': 'Mode Analytics / W3Schools',
                'category': 'SQL & Databases',
                'skill': 'SQL',
                'difficulty': 'Beginner',
                'external_url': 'https://mode.com/sql-tutorial/',
                'description': 'Interactive SQL tutorial covering aggregations, subqueries, complex JOINs, window functions, and performance tuning.',
                'is_free': True,
                'resource_type': 'Documentation',
                'duration': '5 hours',
                'why_recommended': 'SQL is currently unassessed and required for modern software development.'
            },
            {
                'title': 'MDN Web Docs: Modern Web Development Foundations',
                'provider': 'Mozilla Developer Network',
                'category': 'Web Development',
                'skill': 'Web Development',
                'difficulty': 'Beginner',
                'external_url': 'https://developer.mozilla.org/en-US/docs/Learn',
                'description': 'Authoritative industry standard tutorials for semantic HTML5, modern responsive CSS, JavaScript APIs, and accessibility.',
                'is_free': True,
                'resource_type': 'Documentation',
                'duration': '8 hours',
                'why_recommended': 'Directly aligns with your interested domain in Web Development.'
            },
            {
                'title': 'Git & GitHub Crash Course for Developers',
                'provider': 'freeCodeCamp',
                'category': 'Tools & DevOps',
                'skill': 'Git/GitHub',
                'difficulty': 'Intermediate',
                'external_url': 'https://www.youtube.com/watch?v=RGOj5yH7evk',
                'description': 'Master branch rebasing, merge conflict resolution, pull request workflows, tags, and GitHub collaborative actions.',
                'is_free': True,
                'resource_type': 'Video',
                'duration': '2 hours',
                'why_recommended': 'Level up your verified Git score (currently 58/100) to professional readiness.'
            },
            {
                'title': 'Effective Communication for Engineers',
                'provider': 'Google Tech Writing',
                'category': 'Communication & Soft Skills',
                'skill': 'Communication',
                'difficulty': 'Intermediate',
                'external_url': 'https://developers.google.com/tech-writing',
                'description': 'Free industry technical writing and architectural communication course designed by Google engineering leads.',
                'is_free': True,
                'resource_type': 'Course',
                'duration': '3 hours',
                'why_recommended': 'Reinforces high verified communication competency.'
            },
            {
                'title': 'Competitive Programming & Problem Solving Patterns',
                'provider': 'LeetCode Explore',
                'category': 'Problem Solving',
                'skill': 'Problem Solving',
                'difficulty': 'Intermediate',
                'external_url': 'https://leetcode.com/explore/',
                'description': 'Curated coding challenges, two-pointer techniques, sliding windows, and greedy problem-solving patterns.',
                'is_free': True,
                'resource_type': 'Practice',
                'duration': 'Ongoing',
                'why_recommended': 'High skill gap in Problem Solving for your Software Developer goal.'
            }
        ]

        for r_item in resources_seed:
            sk = skills_dict.get(r_item['skill'])
            if sk:
                res = LearningResource(
                    title=r_item['title'],
                    provider=r_item['provider'],
                    category=r_item['category'],
                    skill_id=sk.id,
                    difficulty=r_item['difficulty'],
                    external_url=r_item['external_url'],
                    description=r_item['description'],
                    is_free=r_item['is_free'],
                    resource_type=r_item['resource_type'],
                    duration=r_item['duration'],
                    why_recommended=r_item['why_recommended']
                )
                db.session.add(res)

        # -------------------------------------------------------------
        # 7. SEED REAL-WORLD VERIFIABLE OPPORTUNITIES
        # -------------------------------------------------------------
        opportunities_seed = [
            {
                'company_name': 'Demo Tech Solutions',
                'company_id': industry_profile.id,
                'title': 'Python Developer Intern',
                'description': 'Join our core platform engineering team in Hyderabad to develop backend microservices, implement asynchronous task processing with Redis/Celery, and build RESTful endpoints. You will collaborate with senior system architects and participate in peer code reviews.',
                'opportunity_type': 'internship',
                'location': 'Hyderabad, India',
                'work_mode': 'Hybrid',
                'duration': '3 months',
                'experience_level': 'Fresher (0-1 years)',
                'eligibility': '2nd-4th year students (CSE/IT/ECE)',
                'deadline': '2026-10-31',
                'stipend_salary': '₹25,000 / month',
                'required_skills': ['Python', 'Data Structures', 'Git/GitHub', 'Problem Solving'],
                'required_skill_levels': ['intermediate', 'intermediate', 'beginner', 'intermediate'],
                'application_questions': [
                    {'id': 1, 'question_text': 'Why are you interested in this engineering role at Demo Tech Solutions?', 'is_required': True},
                    {'id': 2, 'question_text': 'Describe a complex problem or project where you utilized Python data structures.', 'is_required': True}
                ],
                'source_url': 'https://demotech.example.com/careers/python-intern',
                'date_retrieved': 'Verified 2 days ago'
            },
            {
                'company_name': 'Tata Consultancy Services',
                'company_id': None,
                'title': 'Software Engineering Trainee (Full-Stack)',
                'description': 'TCS Innovation Labs is seeking motivated student developers proficient in enterprise systems, relational database modeling, and modern web application frontends. Work on live industry transformation assignments with global clients.',
                'opportunity_type': 'full-time',
                'location': 'Bengaluru, India',
                'work_mode': 'On-site',
                'duration': 'Full-time',
                'experience_level': 'Fresher',
                'eligibility': 'Final year B.Tech / M.Tech students',
                'deadline': '2026-11-15',
                'stipend_salary': '₹4,50,000 - ₹7,00,000 / year',
                'required_skills': ['C Programming', 'Data Structures', 'SQL', 'Communication'],
                'required_skill_levels': ['intermediate', 'intermediate', 'intermediate', 'intermediate'],
                'application_questions': [
                    {'id': 1, 'question_text': 'Summarize your experience building relational database queries.', 'is_required': True}
                ],
                'source_url': 'https://www.tcs.com/careers',
                'date_retrieved': 'Verified 3 days ago'
            },
            {
                'company_name': 'Amazon Web Services',
                'company_id': None,
                'title': 'Cloud Support & Development Intern',
                'description': 'AWS Cloud Support Interns solve distributed computing challenges, optimize cloud resources, and debug automated deployment scripts. Mentorship provided by experienced AWS Solutions Architects.',
                'opportunity_type': 'internship',
                'location': 'Hyderabad, India',
                'work_mode': 'Hybrid',
                'duration': '6 months',
                'experience_level': 'Fresher',
                'eligibility': '3rd or 4th year undergraduate students',
                'deadline': '2026-10-25',
                'stipend_salary': '₹45,000 / month',
                'required_skills': ['Cloud Computing', 'Python', 'Git/GitHub', 'Problem Solving'],
                'required_skill_levels': ['intermediate', 'intermediate', 'intermediate', 'intermediate'],
                'application_questions': [
                    {'id': 1, 'question_text': 'What AWS services or cloud concepts are you most comfortable with?', 'is_required': True},
                    {'id': 2, 'question_text': 'Share a link to your GitHub repository demonstrating cloud or scripting work.', 'is_required': False}
                ],
                'source_url': 'https://amazon.jobs/en/jobs/cloud-intern',
                'date_retrieved': 'Verified 1 day ago'
            },
            {
                'company_name': 'Infosys Limited',
                'company_id': None,
                'title': 'Junior Data Analyst Apprentice',
                'description': 'Analyze customer transaction patterns, build automated data ingestion scripts, and generate interactive visual performance dashboards for enterprise stakeholders.',
                'opportunity_type': 'apprenticeship',
                'location': 'Pune, India',
                'work_mode': 'Remote',
                'duration': '4 months',
                'experience_level': 'Fresher',
                'eligibility': '2nd to 4th year students with strong statistical foundation',
                'deadline': '2026-10-20',
                'stipend_salary': '₹22,000 / month',
                'required_skills': ['SQL', 'Python', 'Statistics', 'Communication'],
                'required_skill_levels': ['intermediate', 'beginner', 'intermediate', 'intermediate'],
                'application_questions': [
                    {'id': 1, 'question_text': 'Explain a situation where you had to derive insights from noisy data.', 'is_required': True}
                ],
                'source_url': 'https://www.infosys.com/careers',
                'date_retrieved': 'Verified 4 days ago'
            }
        ]

        for opp_data in opportunities_seed:
            opp = Opportunity(
                company_id=opp_data['company_id'],
                company_name=opp_data['company_name'],
                title=opp_data['title'],
                description=opp_data['description'],
                opportunity_type=opp_data['opportunity_type'],
                location=opp_data['location'],
                work_mode=opp_data['work_mode'],
                duration=opp_data['duration'],
                experience_level=opp_data['experience_level'],
                eligibility=opp_data['eligibility'],
                deadline=opp_data['deadline'],
                stipend_salary=opp_data['stipend_salary'],
                source_url=opp_data['source_url'],
                date_retrieved=opp_data['date_retrieved'],
                status='published'
            )
            opp.required_skills = opp_data['required_skills']
            opp.required_skill_levels = opp_data['required_skill_levels']
            opp.application_questions = opp_data['application_questions']
            db.session.add(opp)

        # -------------------------------------------------------------
        # 8. SEED ACADEMICIAN COLLABORATIONS & OPPORTUNITIES
        # -------------------------------------------------------------
        collabs_seed = [
            {
                'academician_id': academician_profile.id,
                'industry_id': industry_profile.id,
                'institution_id': institution_profile.id,
                'title': 'Generative AI Applications in Cloud Systems',
                'collaboration_type': 'Guest Lecture Series',
                'description': 'Deliver a 3-part guest lecture series on LLM architectures, context engineering, and distributed deployment for undergraduate computer science students.',
                'duration': '3 Weeks (1 session/week)',
                'commitment': '2 hours/week',
                'skills_needed': 'GenAI, Cloud Architecture, Python',
                'deliverables': 'Lecture slide deck, live coding demo, student Q&A recording',
                'status': 'Active'
            },
            {
                'academician_id': academician_profile.id,
                'industry_id': industry_profile.id,
                'institution_id': institution_profile.id,
                'title': 'Autonomous Edge Computing Lab Mentorship',
                'collaboration_type': 'Live Projects',
                'description': 'Joint industry-faculty mentorship for student senior capstone projects focusing on latency-sensitive IoT streaming.',
                'duration': '1 Semester',
                'commitment': '3 hours/week',
                'skills_needed': 'C/C++, Distributed Systems, IoT Protocols',
                'deliverables': 'Prototype validation report, capstone project evaluation',
                'status': 'Proposed'
            }
        ]

        for c_data in collabs_seed:
            collab = Collaboration(
                academician_id=c_data['academician_id'],
                industry_id=c_data['industry_id'],
                institution_id=c_data['institution_id'],
                title=c_data['title'],
                collaboration_type=c_data['collaboration_type'],
                description=c_data['description'],
                duration=c_data['duration'],
                commitment=c_data['commitment'],
                skills_needed=c_data['skills_needed'],
                deliverables=c_data['deliverables'],
                status=c_data['status']
            )
            db.session.add(collab)

        # -------------------------------------------------------------
        # 9. SEED INITIAL NOTIFICATIONS
        # -------------------------------------------------------------
        n1 = Notification(
            user_id=student_user.id,
            event_type='welcome',
            message='Welcome to SkillBridge! Your verified skill profile and career goal have been initialized.',
            read=False,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        n2 = Notification(
            user_id=student_user.id,
            event_type='skill_recommendation',
            message='New Python and Data Structures assessments are available to strengthen your Software Developer readiness.',
            read=False,
            created_at=datetime.utcnow() - timedelta(hours=5)
        )
        n3 = Notification(
            user_id=industry_user.id,
            event_type='welcome',
            message='Demo Tech Solutions company profile is active. You can now publish opportunities and discover qualified candidates.',
            read=False,
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        n4 = Notification(
            user_id=academician_user.id,
            event_type='collaboration_invitation',
            message='Demo Tech Solutions confirmed your Guest Lecture Series proposal for Fall 2026.',
            read=False,
            created_at=datetime.utcnow() - timedelta(hours=8)
        )
        n5 = Notification(
            user_id=institution_user.id,
            event_type='analytics_summary',
            message='Institutional analytics updated: 75 students assessed across 12 skills.',
            read=False,
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add_all([n1, n2, n3, n4, n5])

        db.session.commit()
        print("Database seeded successfully with realistic demo accounts, verified skills, assessments, resources, and opportunities.")


def ensure_assessment_catalog(app):
    """Ensure every shared skill has a small, usable demo assessment catalog."""
    with app.app_context():
        for skill in Skill.query.order_by(Skill.id).all():
            assessment = Assessment.query.filter_by(skill_id=skill.id).first()
            if assessment is None:
                assessment = Assessment(
                    skill_id=skill.id,
                    difficulty='medium',
                    title=f'{skill.name} Demo Assessment',
                    instructions=f'Answer at least three demo questions about {skill.name}.',
                    time_limit_mins=15
                )
                db.session.add(assessment)
                db.session.flush()

            question_count = assessment.questions.count()
            demo_questions = [
                (f'Which statement best describes {skill.name}?', [f'It is a core {skill.category} competency', 'It is only a file format', 'It is a database table', 'It is a network protocol']),
                (f'Which is a useful way to improve {skill.name}?', ['Practice with feedback and review', 'Avoid examples entirely', 'Skip foundational concepts', 'Use unrelated shortcuts']),
                (f'Why is {skill.name} useful in a professional setting?', ['It supports measurable, repeatable work', 'It removes the need for communication', 'It guarantees every result', 'It applies only outside technology'])
            ]
            for index in range(question_count, 3):
                question_text, options = demo_questions[index]
                question = AssessmentQuestion(
                    assessment_id=assessment.id,
                    question_text=question_text,
                    correct_option_index=0,
                    explanation=f'This demo assessment uses the first option as the correct answer for {skill.name}.',
                    difficulty='medium',
                    topic='Foundations'
                )
                question.options = options
                db.session.add(question)

        db.session.commit()

if __name__ == '__main__':
    seed_database()
