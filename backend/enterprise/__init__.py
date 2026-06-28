# Enterprise modules for DecisionOS
# This package is NOT included in the open-source version.
# It provides paid features via a plugin mechanism.

from __future__ import annotations
from typing import Any

# Feature flags - enterprise sets these
FEATURES: dict[str, bool] = {
    "llm_scoring": False,       # Real LLM scoring (vs keyword matching)
    "custom_packs": False,      # User-defined custom Packs
    "private_cases": False,     # Import private business cases
    "team_sso": False,          # Team accounts & SSO
    "enterprise_integrations": False,  # Lark/WeCom/DingTalk
    "enhanced_pdf": False,      # Advanced PDF export
}

def check_feature(name: str) -> bool:
    """Check if an enterprise feature is available."""
    return FEATURES.get(name, False)
