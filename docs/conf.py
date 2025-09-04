# docs/conf.py
from __future__ import annotations

import os
import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version

# Ensure project root is importable (autodoc)
sys.path.insert(0, os.path.abspath(".."))

project = "dictutils"
author = "Adi Eyal"
current_year = datetime.now().year
copyright = f"{current_year}, {author}"
try:
    release = version("dictutils")
except PackageNotFoundError:
    release = "dev"

# Version without extra metadata for display
version = release.split("+")[0] if "+" in release else release

# Extensions
extensions = [
    "myst_parser",  # Markdown support
    "sphinx.ext.autodoc",  # API docs from docstrings
    "sphinx.ext.autosummary",  # Summary tables and stub gen
    "sphinx.ext.napoleon",  # Google/NumPy docstrings
    "sphinx.ext.intersphinx",  # Cross-project links
    "sphinx.ext.viewcode",  # Link to source
    "sphinx_copybutton",  # Copy code buttons
    "sphinx_autodoc_typehints",  # Render type hints nicely
]

# MyST (Markdown) config
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3  # anchor headings up to ### by default

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst",
}

# Autosummary
autosummary_generate = True
autodoc_typehints = "description"  # show type hints in description
autodoc_member_order = "bysource"  # keep source order

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# HTML theme
html_theme = "alabaster"
html_static_path = ["_static"]
templates_path = ["_templates"]

# Alabaster theme options
html_theme_options = {
    "github_user": "adieyal",
    "github_repo": "dictutils",
    "github_button": True,
    "github_banner": True,
    "github_type": "star",
    "show_powered_by": False,
    "show_related": False,
    "note_bg": "#FFF59C",
    "page_width": "1024px",
    "sidebar_width": "300px",
    "fixed_sidebar": True,
    "description": "Small, dependency-free utilities for nested dictionaries",
    "extra_nav_links": {
        "📦 PyPI Package": "https://pypi.org/project/dictutils/",
        "🐛 Issue Tracker": "https://github.com/adieyal/dictutils/issues",
        "📖 Changelog": "https://github.com/adieyal/dictutils/blob/master/CHANGELOG.md",
    }
}

# Keep warnings loud on RTD
nitpicky = False

# Linkcheck tuning
linkcheck_ignore = [
    r"https://localhost[:/].*",
]
linkcheck_timeout = 10
linkcheck_workers = 4
