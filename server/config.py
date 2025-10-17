"""
Server Configuration - Wrapper around unified_config.py
This file maintains backward compatibility with existing code
All settings are now loaded from config.yaml
"""

# Import from unified config
from unified_config import *  # noqa: F403, F401

# This file now simply re-exports everything from unified_config
# All configuration should be edited in config.yaml
