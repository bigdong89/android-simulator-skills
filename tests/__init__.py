#!/usr/bin/env python3
"""
Unit tests package for Android Simulator Skills

This package contains comprehensive unit tests for all core scripts
in the Android Simulator Skills framework.

Test modules:
- test_common_utils.py: Tests for unified error handling and logging
- test_navigator.py: Tests for UI navigation and element interaction
- test_screen_mapper.py: Tests for screen analysis and element parsing
- test_accessibility_audit.py: Tests for WCAG accessibility compliance
- test_app_launcher.py: Tests for app management and launching

Running tests:
    # Run all tests
    python -m pytest tests/

    # Run specific test file
    python -m pytest tests/test_common_utils.py

    # Run with coverage
    python -m pytest tests/ --cov=scripts --cov-report=html

    # Run specific test
    python -m pytest tests/test_navigator.py::TestAndroidNavigator::test_fuzzy_text_match
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

__version__ = "1.0.0"
__test_suite__ = "Android Simulator Skills Unit Tests"
__coverage_target__ = 90.0