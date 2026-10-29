import pandas as pd


def analyze_timing(
    supplier_analysis,
    negotiation_case
):
    """
    Analyze supplier timing and delivery dependency.

    Prototype implementation for timing / hold-up analysis.

    The model compares:
        1. Supplier lead time
        2. Quoted delivery time
        3. Buyer's required delivery time

    This identifies timing dependency and delivery risk.
    It does NOT prove supplier hold-up behaviour.
    """

    result = supplier_analysis.copy()

    # ------------------------------------------------------
    # Required delivery time
    # ------------------------------------------------------

    required_delivery_days = negotiation_case.iloc[0][
        "required_delivery_days"
    ]

    # ------------------------------------------------------
    # Lead-time gap
    # ------------------------------------------------------

    result["lead_time_gap"] = (
        result["lead_time_days"]
        - required_delivery_days
    )

    # ------------------------------------------------------
    # Quoted delivery gap
    # ------------------------------------------------------

    result["delivery_gap"] = (
        result["delivery_days"]
        - required_delivery_days
    )

    # ------------------------------------------------------
    # Timing dependency
    # ------------------------------------------------------

    result["timing_dependency"] = (
        result["delivery_gap"]
        .clip(lower=0)
    )

    # ------------------------------------------------------
    # Timing risk classification
    # ------------------------------------------------------

    def classify_timing(row):

        lead_gap = row["lead_time_gap"]
        delivery_gap = row["delivery_gap"]

        # Both supplier lead time and quotation
        # meet the buyer's requirement.
        if lead_gap <= 0 and delivery_gap <= 0:
            return "Low Timing Risk"

        # Supplier is within 5 days of the
        # buyer's required delivery.
        elif lead_gap <= 5 and delivery_gap <= 5:
            return "Moderate Timing Risk"

        # Larger timing dependency.
        else:
            return "High Timing Risk"

    result["timing_risk"] = result.apply(
        classify_timing,
        axis=1
    )

    return result[
        [
            "supplier_id",
            "supplier_name",
            "lead_time_days",
            "delivery_days",
            "lead_time_gap",
            "delivery_gap",
            "timing_dependency",
            "timing_risk"
        ]
    ]


# ----------------------------------------------------------
# Compatibility function
# ----------------------------------------------------------
# Some versions of negotiation_decision.py may call
# calculate_timing_analysis().
# Keep this wrapper so both function names work.

def calculate_timing_analysis(
    supplier_analysis,
    negotiation_case
):
    return analyze_timing(
        supplier_analysis,
        negotiation_case
    )


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("\n========================================")
    print(" TIMING / HOLD-UP ANALYSIS")
    print("========================================\n")

    # ------------------------------------------------------
    # Load data
    # ------------------------------------------------------

    supplier_data = pd.read_csv(
        "data/sample/supplier_data.csv"
    )

    purchase_history = pd.read_csv(
        "data/sample/purchase_history.csv"
    )

    quotation_data = pd.read_csv(
        "data/sample/quotation_data.csv"
    )

    negotiation_case = pd.read_csv(
        "data/sample/negotiation_case.csv"
    )

    # ------------------------------------------------------
    # Supplier Analysis
    # ------------------------------------------------------

    from supplier_analysis import analyze_suppliers

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    # ------------------------------------------------------
    # Timing Analysis
    # ------------------------------------------------------

    timing_result = analyze_timing(
        supplier_analysis,
        negotiation_case
    )

    print(
        timing_result.to_string(
            index=False
        )
    )

    print("\n========================================")
    print(" TIMING ANALYSIS COMPLETED")
    print("========================================\n")