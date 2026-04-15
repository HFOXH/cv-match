"""Central registry of all OpenAI prompts used by the backend.

Keeping prompts in one file makes it easier to audit wording, tune behavior,
and see the full conversational surface the model is exposed to.

Each prompt is a module-level constant. User prompts that contain
placeholders use ``str.format`` — literal braces in the JSON schema blocks
are doubled (``{{`` / ``}}``) so ``.format()`` leaves them intact.
"""


# CV parsing  (cv_processor/parsers/openai_parser.py)


K_CV_PARSER_SYSTEM_PROMPT = """You are a CV/resume parser. Extract structured information from the provided CV text.
Always respond with valid JSON matching the exact schema provided.
If a field cannot be determined from the text, use null for single values or empty arrays for lists.
Do not invent or hallucinate information — only extract what is explicitly present in the text."""

K_CV_PARSER_USER_PROMPT = """Parse the following CV/resume text and extract structured information.

IMPORTANT: For the "skills" field, extract ALL skills from the ENTIRE CV — this applies to ANY industry (retail, healthcare, trades, IT, hospitality, etc.):
- Explicit skills/qualifications sections
- Skills demonstrated in job responsibilities (e.g., "managed inventory" → "inventory management", "operated cash register" → "cash handling", "prepared food items" → "food preparation")
- Soft skills shown through experience (e.g., working in teams → "teamwork", handling customers → "customer service", juggling multiple tasks → "multitasking")
- Certifications and course titles (e.g., "Food Safety Certificate" → "food safety", "First Aid" → "first aid")
- Education field names (e.g., "Diploma in Culinary Arts" → "culinary arts", "Software Engineering" → "software engineering")
- Tools, equipment, or systems mentioned (e.g., "POS systems", "forklift", "Excel", "SAP")
Do not limit extraction to just the Skills section. Extract from ALL sections.

Return a JSON object with this exact schema:
{{
    "contact": {{
        "name": "Full name or null",
        "email": "Email address or null",
        "phone": "Phone number or null",
        "location": "City/Country or null",
        "linkedin": "LinkedIn URL or null"
    }},
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "job_title": "Title",
            "company": "Company name",
            "start_date": "Start date as written",
            "end_date": "End date as written or 'Present'",
            "description": "Brief description of role/responsibilities"
        }}
    ],
    "education": [
        {{
            "degree": "Degree name",
            "institution": "School/University name",
            "year": "Graduation year or date range",
            "field": "Field of study or null"
        }}
    ],
    "certifications": ["cert1", "cert2", ...],
    "summary": "Professional summary/objective if present, or null",
    "education_level": "The candidate's HIGHEST education level. Must be one of: 'phd', 'masters', 'bachelors', 'college diploma', 'high school', or null if unknown"
}}

CV TEXT:
---
{cv_text}
---

Return ONLY the JSON object, nothing else."""


# CV normalization  (nlp_preprocessing/cv_normalizer.py)


K_NORMALIZATION_SYSTEM_PROMPT = (
    "You are a CV data normalizer. Return only valid JSON, no markdown."
)

K_NORMALIZATION_USER_PROMPT = """Normalize this parsed CV data for job matching purposes.
Return ONLY valid JSON with these fields:

{{
    "skills": ["list of normalized, deduplicated skill names in lowercase"],
    "experience_text": "single paragraph combining all work experience for semantic embedding",
    "education_text": "single paragraph combining all education for semantic embedding",
    "full_text_for_embedding": "complete natural-language summary of the candidate combining all sections"
}}

Rules for skills normalization:
- Lowercase all skill names
- Expand common abbreviations from ANY industry (JS -> javascript, ML -> machine learning, AWS -> amazon web services, POS -> point of sale, CPR -> cardiopulmonary resuscitation, HVAC -> heating ventilation and air conditioning, etc.)
- Merge duplicates
- Keep both technical/hard skills AND soft skills
- Remove non-skill items if any
- Split compound skills into individual entries (e.g., "teamwork and communication" -> "teamwork", "communication")
- Infer implicit skills clearly demonstrated by experience (e.g., working retail -> "multitasking", "time management", "attention to detail"; managing stock -> "inventory management"; serving customers -> "customer service")
- Include common soft skills that are clearly demonstrated by the experience even if not explicitly listed
- This applies to ALL industries: retail, healthcare, trades, hospitality, IT, education, manufacturing, etc.

Rules for text fields:
- Write experience_text as a factual summary of capabilities and domains: focus on years of experience, types of roles held, industries/domains, and key responsibilities. Examples: "2+ years of retail experience as a store associate at a grocery chain. Handled customer service, food preparation, stock rotation, and merchandising." or "5 years of nursing experience in acute care settings. Skilled in patient assessment, medication administration, and electronic health records."
- Write education_text as a factual summary of qualifications: focus on degree levels, fields of study, and institutions. Examples: "Software Engineering Technology diploma from Conestoga College. Currently pursuing AI and ML at Cambrian College." or "Bachelor of Science in Nursing from University of Toronto. CPR and First Aid certified."
- The full_text_for_embedding should read like a professional profile summary
- All text fields should use neutral, factual language that works for both CV-to-JD and JD-to-CV comparison

Parsed CV data:
{cv_data}"""



# Job description extraction  (nlp_preprocessing/job_preprocessor.py)


K_EXTRACTION_SYSTEM_PROMPT = (
    "You are a precise job description parser. Return only valid JSON, no markdown."
)

K_EXTRACTION_USER_PROMPT = """Analyze this job description and extract structured information.
Return ONLY valid JSON with these fields:

{{
    "required_skills": ["skills explicitly marked as required/must-have"],
    "preferred_skills": ["skills marked as preferred/nice-to-have/bonus"],
    "experience_years": "experience requirement as string (e.g., '3-5 years') or null",
    "education_level": "highest education mentioned (PhD/Master's/Bachelor's) or null",
    "experience_requirements": "Factual summary of experience needed: years of experience, types of roles, domains, and key responsibilities. Use neutral language. Examples: '1-2 years of retail or customer service experience preferred.' or '3+ years of full stack development experience.' If none found, use null.",
    "education_requirements": "Factual summary of education needed: degree levels, fields of study, certifications. Use neutral language. Examples: 'High school diploma or equivalent.' or 'Bachelor's degree in Computer Science or related field.' If none found, use null.",
    "key_phrases": ["important multi-word phrases that capture the role essence, e.g., 'retail store associate', 'customer service', 'food safety compliance', 'project management'"],
    "summary": "Concise summary of the job description, max 250 words"
}}

Rules:
- Normalize skill names from ANY industry (e.g., 'JS' -> 'JavaScript', 'POS' -> 'point of sale', 'CPR' -> 'CPR certification')
- If a skill is not clearly required or preferred, put it in required_skills
- Include both hard skills (tools, certifications, technical abilities) and soft skills (communication, leadership, teamwork, multitasking)
- This applies to ALL industries: retail, healthcare, trades, hospitality, IT, education, manufacturing, etc.
- Do NOT include physical requirements as skills (e.g., "ability to stand for extended periods", "ability to lift 50 lbs", "ability to work in cold environments", "physical stamina"). These are working conditions, not skills.
- Do NOT include generic availability requirements as skills (e.g., "flexible schedule", "available weekends")
- Key phrases should be bigrams/trigrams that capture the role essence
- Summary should be clear, professional, and no more than 250 words

Job Description:
{jd_text}"""



# Semantic skill matching  (services/similarity_engine.py)


K_SEMANTIC_MATCH_PROMPT = """Given these two skill lists, find pairs where the CV skill satisfies or strongly overlaps with the JD skill.

CV skills (candidate has): {cv_skills}
JD skills (job requires): {jd_skills}

Return ONLY valid JSON — a list of matched pairs where the CV skill demonstrates the JD requirement:
{{"matches": [["cv_skill", "jd_skill"], ...]}}

Rules:
- Match skills that are equivalent, synonymous, or where the CV skill clearly demonstrates the JD requirement
- Examples across industries:
  - "teamwork" or "team collaboration" matches "interpersonal skills"
  - "customer focused service" matches "customer service"
  - "food preparation and handling" matches "food handling"
  - "quality control" or "compliance awareness" matches "attention to detail"
  - "stock rotation" or "stock management" matches "inventory management"
  - "patient care" matches "healthcare delivery"
  - "cash handling" matches "point of sale" or "POS"
- A skill that is a subset or specialization of the required skill counts as a match
- Do NOT match skills that are merely in the same domain but unrelated (e.g., "Python" and "JavaScript", "cooking" and "cleaning")
- If no semantic matches exist, return {{"matches": []}}"""
