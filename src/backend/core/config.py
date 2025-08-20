#!/usr/bin/env python3
"""
Configuration and constants for Resume Workshop
"""

import os

# Server configuration
PORT = 8081
WORKSHOP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directory paths
VARIANTS_DIR = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants')
TEMPLATES_DIR = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'templates')
OUTPUT_DIR = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'output')
JOB_DESCRIPTIONS_DIR = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'job_descriptions')
QUALITY_FEEDBACK_DIR = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'quality_feedback')

# Optional features
try:
    import requests
    from bs4 import BeautifulSoup
    LINKEDIN_SUPPORT = True
except ImportError:
    LINKEDIN_SUPPORT = False

# Background job configuration
MAX_WORKERS = 3
JOB_TIMEOUT = 600  # 10 minutes