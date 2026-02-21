"""Test whether the SkillsParser is using spaCy or the regex fallback."""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from nlp.parsers.skills_parser import SkillsParser


def main():
    # Force initialization
    SkillsParser._ensure_initialized()

    print("=== spaCy Status ===")
    print(f"  spaCy available:    {SkillsParser._use_spacy}")
    print(f"  NLP model loaded:   {SkillsParser._nlp is not None}")
    print(f"  PhraseMatcher ready: {SkillsParser._matcher is not None}")

    if SkillsParser._use_spacy:
        model = SkillsParser._nlp.meta
        print(f"  Model: {model['name']} v{model['version']}")
        print(f"  Patterns loaded: {len(SkillsParser.SKILLS_DATABASE)}")

        # Tokenization test — spaCy keeps these as single tokens
        doc = SkillsParser._nlp("I know C++ and Node.js and .NET")
        print(f"\n=== Tokenization Test ===")
        print(f"  Input:  'I know C++ and Node.js and .NET'")
        print(f"  Tokens: {[t.text for t in doc]}")

        # Skill matching test
        test_text = "Experienced in Python, machine learning, and React Native development"
        skills = SkillsParser.extract(test_text)
        print(f"\n=== Skill Matching Test ===")
        print(f"  Input: '{test_text}'")
        print(f"  Found: {sorted(skills)}")
    else:
        print("\n  WARNING: spaCy is NOT active — using regex fallback!")
        print("  To fix, run:")
        print("    pip install spacy")
        print("    python -m spacy download en_core_web_sm")


if __name__ == "__main__":
    main()
