"""
Fuzzy duplicate detection for metric registration.
Simulates the AI-powered dedup capability of the Semantics Reconciliation Engine.
"""

from rapidfuzz import fuzz


def detect_duplicates(
    proposed_name: str,
    proposed_description: str,
    proposed_calculation: str,
    metrics: list,
    threshold: int = 60,
    max_results: int = 5,
) -> list[dict]:
    """
    Compare a proposed metric against the existing registry and return ranked
    potential duplicates above the similarity threshold.

    Scoring:
      - display_name similarity:           30%
      - description similarity:            40%
      - calculation_description similarity: 30%

    Returns a list of dicts sorted by composite_score descending.
    """
    results = []

    name_input = proposed_name.strip()
    desc_input = proposed_description.strip()
    calc_input = proposed_calculation.strip()

    # Need at least the name or one description to search
    if not name_input and not desc_input and not calc_input:
        return []

    for metric in metrics:
        name_score = fuzz.token_set_ratio(name_input, metric.get("display_name", ""))
        desc_score = fuzz.token_set_ratio(desc_input, metric.get("description", ""))
        calc_score = fuzz.token_set_ratio(calc_input, metric.get("calculation_description", ""))

        composite = (name_score * 0.30) + (desc_score * 0.40) + (calc_score * 0.30)

        if composite >= threshold:
            results.append(
                {
                    "metric_id": metric["metric_id"],
                    "display_name": metric["display_name"],
                    "domain_id": metric["domain_id"],
                    "tier": metric["tier"],
                    "status": metric["status"],
                    "similarity_score": round(composite, 1),
                }
            )

    return sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:max_results]
