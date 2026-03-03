from typing import List

# Temporary test version (ML disabled)

def analyze_signal(features: List[float]):

    # Basic validation (optional but good practice)
    if not isinstance(features, list):
        raise ValueError("Features must be a list.")

    # Example length check (optional)
    if len(features) == 0:
        raise ValueError("Features list cannot be empty.")

    # Temporary response
    return {
        "message": "Backend Working - ML Disabled",
        "received_feature_count": len(features)
    }