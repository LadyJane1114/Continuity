"""NSCC Knowledge Base - Formatted for RAG Pipeline"""

# Dataset 1: NSCC Website Pages (Info-based)
nscc_pages_documents = [
    """NSCC is Nova Scotia's community college with 14 campuses and over 20,000 students. It delivers inclusive, flexible, industry-driven education, applied research, and community impact focused on student success, economic development, and workforce needs.""",
    
    """NSCC's Vision is transforming Nova Scotia one learner at a time. Mission: Building Nova Scotia's economy and quality of life through education and innovation. The college's promise is to empower those who strive to know more. Core values include accessibility, diversity, innovation, student success, sustainability, inclusion, teamwork, creativity, public accountability, safety, and employee success.""",
    
    """NSCC offers over 140 certificate and diploma programs ranging from 18 weeks to 3 years, plus continuing education and marine training. Programs span disciplines from trades to health, business, technology, and creative industries.""",
    
    """NSCC supports students through campus life, cultural supports, housing, wellness services, events, tours, and parent resources. The college provides guidance for parents, campus tours, and a main viewbook for prospective students.""",
    
    """NSCC offers comprehensive student support including academic advising, accessibility services, wellness and counselling, learning services, career support, entrepreneurship resources, financial aid, technical help, and specialized supports for equity-deserving groups and military-connected students.""",
    
    """Student advisors at NSCC help students understand program requirements, set goals, access supports, problem-solve, and engage in campus life. Additional specialized supports are available for Black/African Canadian, Mi'kmaw/Indigenous, 2SLGBTQ+, and international students.""",
    
    """For students with diagnosed physical, mental health, chronic, or learning disabilities, NSCC offers academic accommodations, technological assistance, and barrier-free learning through collaborative planning with the Accessibility Services office.""",
    
    """NSCC provides free, confidential accessibility services including academic accommodations, assistive technologies, and help applying for grants. Students are advised to register early with Accessibility Services for timely support planning.""",
    
    """NSCC accommodations include alternative formats, extra time on exams, note takers, assistive technology, captions, memory aids, and other customized supports. Students register through Accessibility Services and collaborate with faculty on implementation.""",
    
    """NSCC offers free professional and culturally responsive counselling, campus wellness events, fitness and recreation facilities, dietary options, and online partners including Good2Talk, Togetherall, and Tranquility for mental health support.""",
    
    """NSCC learning supports include Peer Assisted Learning (PALS), tutoring, Writing Centres, English as Additional Language (EAL) support, library resources, and testing centres for accommodated test-taking.""",
    
    """NSCC provides job postings, career guidance, resume and cover letter support, GradWorks employer-funded placements, career quizzes, and resources through the Student Career Hub and library guides to support graduate employment.""",
    
    """The NSCC Technology Service Desk provides support for passwords, email, printing, conferencing, network, security, and software issues. Available Monday to Friday 8am–4pm with after-hours monitoring and remote support options.""",
]

nscc_pages_metadata = [
    {"source": "about_nscc", "category": "general"},
    {"source": "vision_mission_values", "category": "general"},
    {"source": "programs_courses", "category": "academics"},
    {"source": "student_experience", "category": "student_life"},
    {"source": "student_supports_overview", "category": "support"},
    {"source": "student_advisors", "category": "support"},
    {"source": "accessibility_services", "category": "support"},
    {"source": "accessibility_supports", "category": "support"},
    {"source": "accommodations", "category": "support"},
    {"source": "wellness_counselling", "category": "support"},
    {"source": "learning_support", "category": "support"},
    {"source": "career_services", "category": "support"},
    {"source": "technical_support", "category": "technical"},
]

# Dataset 2: NSCC FAQ (Q&A-based)
nscc_faq_documents = [
    """NSCC is Nova Scotia's community college with 14 campuses and over 20,000 students. It focuses on inclusive, flexible, industry-driven education and applied research to meet workforce needs and support economic development.""",
    
    """NSCC's Vision is transforming Nova Scotia one learner at a time. The Mission is building Nova Scotia's economy and quality of life through education and innovation.""",
    
    """NSCC upholds the following core values: accessibility, diversity, innovation, student success, sustainability, inclusion, teamwork, creativity, public accountability, safety, and employee success.""",
    
    """NSCC offers over 140 certificate and diploma programs ranging from 18 weeks to 3 years in duration, plus continuing education and marine training across trades, health, business, technology, and creative industries.""",
    
    """Student supports at NSCC include academic advising, accessibility services, wellness and counselling, learning support, career services, entrepreneurship resources, financial aid, and technical help.""",
    
    """Student advisors assist with understanding program requirements, goal setting, accessing supports, problem-solving, campus engagement, and arranging funding. Specialized advisors also support specific student groups.""",
    
    """NSCC provides academic accommodations, assistive technologies, and barrier-free learning environments for students with diagnosed physical, mental health, chronic, or learning disabilities.""",
    
    """NSCC offers free professional counselling, campus wellness events, fitness facilities, dietary options, and online mental health supports through partners like Good2Talk and Togetherall.""",
    
    """Graduate Employment Services at NSCC offer job postings, resume and cover letter support, career guidance, employer-funded placements through GradWorks, and resources through the Student Career Hub.""",
    
    """The Technology Service Desk helps with passwords, email, printing, conferencing, network issues, and software troubleshooting. Available Monday to Friday 8am–4pm with after-hours monitoring and remote support options.""",
]

nscc_faq_metadata = [
    {"source": "faq_what_is_nscc", "category": "general"},
    {"source": "faq_vision_mission", "category": "general"},
    {"source": "faq_values", "category": "general"},
    {"source": "faq_programs", "category": "academics"},
    {"source": "faq_student_supports", "category": "support"},
    {"source": "faq_advisors", "category": "support"},
    {"source": "faq_accessibility", "category": "support"},
    {"source": "faq_wellness", "category": "support"},
    {"source": "faq_employment", "category": "support"},
    {"source": "faq_tech_support", "category": "technical"},
]

# Dataset 3: Campus Events
events_documents = [
    """Community Cleanup Day - Join us for a day of cleaning our local parks and streets. Date: February 15, 2026 at 10:00 AM. Location: IT Campus, Room B125. Contact: cleanup@example.com. Organized by John Smith.""",
    
    """Charity Run 2026 - Annual 5K run to raise funds for local schools. Date: March 22, 2026 at 9:00 AM. Location: IT Campus, Room C214. Contact: charityrun@example.com. Organized by Lisa Anderson.""",
    
    """Winter Art Exhibition - Display of local artists work featuring paintings, sculptures, and photography. Date: February 1, 2026 at 11:00 AM. Location: IT Campus, Room D327. Contact: artshow@example.com. Organized by David Park.""",
    
    """Tech Networking Night - An evening to connect with local tech professionals and students. Date: February 10, 2026 at 6:00 PM. Location: IT Campus, Room B231. Contact: networking@example.com. Organized by Alex Turner.""",
    
    """Cybersecurity Workshop - Hands-on session on securing web applications and networks. Date: February 18, 2026 at 2:00 PM. Location: IT Campus, Room C312. Contact: cyberworkshop@example.com. Organized by Morgan Lee.""",
    
    """AI Hackathon - 24-hour hackathon focused on building AI-powered solutions. Date: March 1, 2026 at 9:00 AM. Location: IT Campus, Room D215. Contact: aihack@example.com. Organized by Jordan Smith.""",
    
    """Game Development Jam - Collaborate and create games in a fun, competitive environment. Date: March 15, 2026 at 10:00 AM. Location: IT Campus, Room B327. Contact: gamejam@example.com. Organized by Taylor Brooks.""",
    
    """Cloud Computing Seminar - Learn about cloud architecture and deployment strategies. Date: February 25, 2026 at 1:00 PM. Location: IT Campus, Room C125. Contact: cloudseminar@example.com. Organized by Casey Nguyen.""",
]

events_metadata = [
    {"source": "event_1", "category": "events", "event_type": "community", "campus": "IT Campus", "event_date": "2026-02-15"},
    {"source": "event_2", "category": "events", "event_type": "charity", "campus": "IT Campus", "event_date": "2026-03-22"},
    {"source": "event_3", "category": "events", "event_type": "arts", "campus": "IT Campus", "event_date": "2026-02-01"},
    {"source": "event_4", "category": "events", "event_type": "networking", "campus": "IT Campus", "event_date": "2026-02-10"},
    {"source": "event_5", "category": "events", "event_type": "workshop", "campus": "IT Campus", "event_date": "2026-02-18"},
    {"source": "event_6", "category": "events", "event_type": "hackathon", "campus": "IT Campus", "event_date": "2026-03-01"},
    {"source": "event_7", "category": "events", "event_type": "workshop", "campus": "IT Campus", "event_date": "2026-03-15"},
    {"source": "event_8", "category": "events", "event_type": "seminar", "campus": "IT Campus", "event_date": "2026-02-25"},
]


def load_nscc_pages():
    """Load NSCC website pages into knowledge base."""
    from database.vector_db import VectorDB
    import logging
    
    logger = logging.getLogger(__name__)
    db = VectorDB(collection_name="documents")
    
    logger.info(f"Adding {len(nscc_pages_documents)} NSCC website documents...")
    db.add_documents(nscc_pages_documents, metadata=nscc_pages_metadata)
    
    info = db.get_collection_info()
    logger.info(f"Knowledge base now contains {info['document_count']} documents")
    print("✓ NSCC website pages loaded successfully!")
    return db


def load_nscc_faq():
    """Load NSCC FAQ into knowledge base."""
    from database.vector_db import VectorDB
    import logging
    
    logger = logging.getLogger(__name__)
    db = VectorDB(collection_name="documents")
    
    logger.info(f"Adding {len(nscc_faq_documents)} NSCC FAQ documents...")
    db.add_documents(nscc_faq_documents, metadata=nscc_faq_metadata)
    
    info = db.get_collection_info()
    logger.info(f"Knowledge base now contains {info['document_count']} documents")
    print("✓ NSCC FAQ loaded successfully!")
    return db


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from utils.logger import setup_logging
    
    setup_logging()
    
    print("\n=== NSCC Knowledge Base Loader ===")
    print("1. Load NSCC Website Pages (13 documents)")
    print("2. Load NSCC FAQ (10 documents)")
    print("3. Load Both")
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        load_nscc_pages()
    elif choice == "2":
        load_nscc_faq()
    elif choice == "3":
        load_nscc_pages()
        load_nscc_faq()
    else:
        print("Invalid choice")
