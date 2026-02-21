"""Run the CV processor on a given PDF file."""

import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

from nlp.processors.cv_processor import CVProcessor


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_cv_processor.py <path_to_pdf>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = CVProcessor.process_file(file_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
