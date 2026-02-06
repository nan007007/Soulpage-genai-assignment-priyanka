def detect_intent(query: str) -> str:
    q = query.lower()

    if any(k in q for k in [
        "graph", "chart", "plot", "visual", "visualize",
        "recharge", "recharges", "sales", "amount",
        "customer", "plan"
    ]):
        return "sql"

    if any(k in q for k in [
        "policy", "leave", "hr", "sop",
        "it policy", "security", "compliance"
    ]):
        return "policy"

    if any(k in q for k in [
        "trip", "travel", "vacation",
        "itinerary", "tour"
    ]):
        return "travel"

    return "internet"
