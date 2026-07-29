"""Skill overlap, experience match, education match between a resume and a job."""

import re

# A basic list of common tech/business skills to extract from the resume directly
COMMON_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "html", "css", "sql", "mysql", "postgresql", "mongodb", "aws", "azure", "gcp",
    "docker", "kubernetes", "linux", "git", "machine learning", "data science", "deep learning",
    "nlp", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "excel", "power bi",
    "tableau", "agile", "scrum", "project management", "communication", "leadership", "sales",
    "marketing", "seo", "digital marketing", "finance", "accounting", "devops", "ci/cd",
    "spring boot", "django", "flask", "ruby on rails", "php", "laravel", "swift", "kotlin",
    "android", "ios", "react native", "flutter", "dart", "golang", "rust", "c", "ruby", "perl",
    "bash", "shell scripting", "powershell", "jira", "confluence", "slack", "trello", "asana",
    "figma", "sketch", "adobe xd", "photoshop", "illustrator", "indesign", "premiere pro",
    "after effects", "lightroom", "blender", "maya", "3ds max", "autocad", "solidworks"
]

def extract_resume_skills(resume_text: str) -> list[str]:
    """Extract known skills from the resume text."""
    text_lower = resume_text.lower()
    found_skills = set()
    
    # We pad the text to help with word boundary matching
    padded_text = f" {text_lower} "
    
    for skill in COMMON_SKILLS:
        # Simple word boundary match
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, padded_text):
            found_skills.add(skill)
            
    return sorted(list(found_skills))


def analyze_skill_gap(resume_text: str, job_skills_str: str) -> dict:
    """
    Compare the resume text against the comma-separated skills required by the job.
    Returns a dict with 'matched' and 'missing' skill lists.
    """
    text_lower = resume_text.lower()
    job_skills = [s.strip().lower() for s in str(job_skills_str).split(',') if s.strip()]
    
    matched = []
    missing = []
    
    for skill in job_skills:
        # Check if the job skill appears in the resume text
        if skill in text_lower:
            matched.append(skill)
        else:
            missing.append(skill)
            
    return {
        "matched": matched,
        "missing": missing
    }
