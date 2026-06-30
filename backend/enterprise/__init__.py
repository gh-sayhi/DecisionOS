"""Open-source enterprise feature boundary for DecisionOS.

The public build keeps enterprise-only implementations out of the repository.
Private deployments can provide their own modules behind these feature flags.
"""

from __future__ import annotations


FEATURES: dict[str, bool] = {
    "llm_scoring": False,
    "custom_packs": False,
    "private_cases": False,
    "team_sso": False,
    "enterprise_integrations": False,
    "enhanced_pdf": False,
    "five_source_engine": False,
}


def check_feature(name: str) -> bool:
    """Return whether an enterprise feature is available in this build."""
    return FEATURES.get(name, False)
