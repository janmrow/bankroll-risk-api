"""
High-level orchestration of analytical bankroll formulas.
Transforms request parameters into deterministic risk and growth metrics.
"""

from app.domain.services.analyze_strategy import analyze_strategy

__all__ = ["analyze_strategy"]
