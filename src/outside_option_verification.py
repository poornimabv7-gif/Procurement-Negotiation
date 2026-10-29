import pandas as pd


def verify_outside_option_signals(credibility_data):
    """
    Apply a verification gate to supplier signals.

    This is a prototype rule-based verification layer.
    It does not claim to prove that a supplier's statement is true.
    """

    result = credibility_data.copy()

    def verification_decision(assessment):

        if pd.isna(assessment):
            return "Unverified - Exclude from Verified Analysis"

        if assessment == "Credible - Can Be Considered":
            return "Verified for Analysis"

        elif assessment == "Partially Credible - Verify":
            return "Requires Verification"

        else:
            return "Unverified - Exclude from Verified Analysis"

    result["verification_decision"] = (
        result["credibility_assessment"]
        .apply(verification_decision)
    )

    return result