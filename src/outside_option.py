import pandas as pd


# ============================================================
# 1. OUTSIDE-OPTION COST CALCULATION
# ============================================================

def calculate_outside_options(
    supplier_analysis,
    market_cost_data,
    required_quantity
):
    """
    Calculate the effective outside-option cost
    for alternative suppliers.

    Prototype formula:

    Effective Outside Option Cost =
        Base Cost
        + Switching Cost
        + Expected Delivery Risk

    Notes:
    - Base cost comes from the supplier quotation.
    - Switching cost is currently a prototype assumption.
    - Delivery risk is currently a prototype assumption.
    - These assumptions should later be calibrated using
      real KB procurement data.
    """

    result = supplier_analysis.copy()

    # ========================================================
    # BASE COST
    # ========================================================

    result["base_cost"] = (
        result["initial_price"] * required_quantity
    )

    # ========================================================
    # SWITCHING COST
    # ========================================================

    # Prototype assumption.
    # This should later come from actual KB data.
    result["switching_cost"] = 20000.0

    # ========================================================
    # EXPECTED DELIVERY RISK
    # ========================================================

    result["expected_delivery_risk"] = 0.0

    if "delivery_feasible" in result.columns:

        result.loc[
            result["delivery_feasible"] == False,
            "expected_delivery_risk"
        ] = 5000.0

    # ========================================================
    # FEASIBILITY
    # ========================================================

    result["feasible"] = (
        result["capacity_feasible"]
        & result["delivery_feasible"]
        & result["qualified"]
    )

    # ========================================================
    # EFFECTIVE OUTSIDE-OPTION COST
    # ========================================================

    result["effective_outside_option_cost"] = (
        result["base_cost"]
        + result["switching_cost"]
        + result["expected_delivery_risk"]
    )

    # ========================================================
    # REMOVE CURRENT SUPPLIER
    # ========================================================

    if "is_current_supplier" in result.columns:

        result = result[
            result["is_current_supplier"] == False
        ].copy()

    # ========================================================
    # KEEP ONLY FEASIBLE ALTERNATIVE SUPPLIERS
    # ========================================================

    result = result[
        result["feasible"] == True
    ].copy()

    # ========================================================
    # SORT BY EFFECTIVE COST
    # ========================================================

    result = result.sort_values(
        by="effective_outside_option_cost",
        ascending=True
    ).reset_index(drop=True)

    return result


# ============================================================
# 2. OUTSIDE-OPTION SIGNAL VERIFICATION
# ============================================================

def verify_outside_option_signals(credibility_data):
    """
    Apply a verification gate to supplier signals.

    This is a prototype rule-based verification layer.

    It does not prove that a supplier statement is true.
    """

    result = credibility_data.copy()

    def verification_decision(assessment):

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


# ============================================================
# 3. STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    supplier_data = pd.read_csv(
        "data/sample/supplier_data.csv"
    )

    quotation_data = pd.read_csv(
        "data/sample/quotation_data.csv"
    )

    purchase_history = pd.read_csv(
        "data/sample/purchase_history.csv"
    )

    negotiation_case = pd.read_csv(
        "data/sample/negotiation_case.csv"
    )

    market_cost_data = pd.read_csv(
        "data/sample/market_cost_data.csv"
    )

    supplier_signals = pd.read_csv(
        "data/sample/supplier_signals.csv"
    )

    # --------------------------------------------------------
    # Import supplier analysis
    # --------------------------------------------------------

    from supplier_analysis import analyze_suppliers

    # --------------------------------------------------------
    # Supplier analysis
    # --------------------------------------------------------

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    # --------------------------------------------------------
    # Required quantity
    # --------------------------------------------------------

    required_quantity = negotiation_case.iloc[0][
        "required_quantity"
    ]

    # --------------------------------------------------------
    # Calculate outside options
    # --------------------------------------------------------

    outside_options = calculate_outside_options(
        supplier_analysis,
        market_cost_data,
        required_quantity
    )

    # --------------------------------------------------------
    # Display outside-option analysis
    # --------------------------------------------------------

    print("\n===== OUTSIDE OPTION ANALYSIS =====\n")

    print(
        outside_options[
            [
                "supplier_id",
                "supplier_name",
                "initial_price",
                "base_cost",
                "switching_cost",
                "expected_delivery_risk",
                "effective_outside_option_cost",
                "feasible"
            ]
        ].to_string(index=False)
    )

    # --------------------------------------------------------
    # Signal verification
    # --------------------------------------------------------

    from signalling import analyze_signals
    from credibility import assess_credibility

    signals = analyze_signals(
        supplier_signals
    )

    credibility = assess_credibility(
        signals
    )

    verification = verify_outside_option_signals(
        credibility
    )

    # --------------------------------------------------------
    # Display verification
    # --------------------------------------------------------

    print("\n===== OUTSIDE OPTION SIGNAL VERIFICATION =====\n")

    print(
        verification[
            [
                "supplier_id",
                "signal_type",
                "signal_value",
                "signal_credibility_score",
                "credibility_assessment",
                "verification_decision"
            ]
        ].to_string(index=False)
    )