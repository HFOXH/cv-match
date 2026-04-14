"""CV parsing using OpenAI GPT-4o-mini.

Authors: Santiago Cardenas and Amel Sunil
First version: 2025-02-27
"""

from .openai_parser import OpenAICVParser, get_parser

__all__ = ["OpenAICVParser", "get_parser"]
