import pandas as pd


def analyze_information_asymmetry(credibility_data):
    """
    Analyze information asymmetry from supplier signal credibility.

    Important:
    - A real supplier signal produces an asymmetry score.
    - No supplier signal does NOT produce a default score.
    - Credibility scores are prototype evidence-strength indicators,
      not calibrated probabilities.
    """

    result = credibility_data.copy()

    # ---------------------------------------------------------
    # Validate required column
    # ---------------------------------------------------------
    if "supplier_id" not in result.columns:
        raise ValueError(
            "information_asymmetry.py requires a 'supplier_id' column."
        )

    if "signal_credibility_score" not in result.columns:
        raise ValueError(
            "information_asymmetry.py requires a "
            "'signal_credibility_score' column."
        )

    # ---------------------------------------------------------
    # Convert credibility score to numeric
    # ---------------------------------------------------------
    result["signal_credibility_score"] = pd.to_numeric(
        result["signal_credibility_score"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # Calculate information asymmetry ONLY when a real
    # credibility signal exists.
    #
    # No signal = NaN, NOT 0.5.
    # ---------------------------------------------------------
    result["information_asymmetry_score"] = float("nan")

    valid_signal_mask = (
        result["signal_credibility_score"].notna()
    )

    result.loc[
        valid_signal_mask,
        "information_asymmetry_score"
    ] = (
        1
        - result.loc[
            valid_signal_mask,
            "signal_credibility_score"
        ]
    )

    # ---------------------------------------------------------
    # Classify asymmetry
    # ---------------------------------------------------------
    def classify_asymmetry(score):

        if pd.isna(score):
            return "No Evidence Available"

        if score >= 0.70:
            return "High Information Asymmetry"

        elif score >= 0.40:
            return "Moderate Information Asymmetry"

        else:
            return "Low Information Asymmetry"

    result["asymmetry_level"] = (
        result["information_asymmetry_score"]
        .apply(classify_asymmetry)
    )

    # ---------------------------------------------------------
    # Recommended action
    # ---------------------------------------------------------
    def recommend_action(level):

        if level == "High Information Asymmetry":
            return (
                "Request evidence before relying on supplier claim"
            )

        elif level == "Moderate Information Asymmetry":
            return (
                "Seek additional information during negotiation"
            )

        elif level == "Low Information Asymmetry":
            return (
                "Information is sufficient for preliminary analysis"
            )

        elif level == "No Evidence Available":
            return (
                "Collect supplier evidence before relying on claims"
            )

        return "Collect additional evidence"

    result["asymmetry_action"] = (
        result["asymmetry_level"]
        .apply(recommend_action)
    )

    # ---------------------------------------------------------
    # Number of actual signals represented by each row
    # ---------------------------------------------------------
    result["information_signal_available"] = (
        result["signal_credibility_score"].notna()
    )

    return result