import pandas as pd


def analyze_signals(supplier_signals):
    """
    Analyze supplier signals using available evidence.

    This is a prototype evidence-strength model.
    It is NOT a calibrated probability of truthfulness.
    """

    signals = supplier_signals.copy()

    # Convert evidence strength to numeric
    signals["evidence_strength"] = pd.to_numeric(
        signals["evidence_strength"],
        errors="coerce"
    )

    # Convert Yes/No evidence availability
    signals["evidence_available_score"] = (
        signals["evidence_available"]
        .str.lower()
        .map({
            "yes": 1.0,
            "no": 0.0
        })
    )

    # Prototype signal credibility indicator
    signals["signal_credibility_score"] = (
        signals["evidence_strength"] *
        signals["evidence_available_score"]
    )

    # Assign an interpretation band
    def classify_signal(score):

        if score >= 0.70:
            return "Strong Evidence"

        elif score >= 0.40:
            return "Partial Evidence"

        else:
            return "Weak / Unverified"

    signals["signal_status"] = (
        signals["signal_credibility_score"]
        .apply(classify_signal)
    )

    return signals


if __name__ == "__main__":

    # Load supplier signals
    supplier_signals = pd.read_csv(
        "data/sample/supplier_signals.csv"
    )

    # Analyze signals
    result = analyze_signals(
        supplier_signals
    )

    print("\n===== SUPPLIER SIGNALLING ANALYSIS =====\n")

    print(
        result[
            [
                "supplier_id",
                "signal_type",
                "signal_value",
                "evidence_available",
                "evidence_strength",
                "signal_credibility_score",
                "signal_status"
            ]
        ].to_string(index=False)
    )