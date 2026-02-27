# /*
# FILE : __init__.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : CV parsing using OpenAI GPT-4o-mini.
# */

from .openai_parser import OpenAICVParser, get_parser, fallback_parse

__all__ = ["OpenAICVParser", "get_parser", "fallback_parse"]
