import pandas as pd


# ============================================================
# SUPPLIER RISK ANALYSIS
# ============================================================

def calculate_supplier_risk(
    supplier_analysis,
    delivery_kpis,
    quotation_kpis,
    timing_analysis=None,
    information_asymmetry=None
):
    """
    Calculate an overall supplier risk score using multiple
    procurement risk dimensions.

    Risk dimensions:
        Delivery Risk              25%
        Quotation Slippage Risk    15%
        Timing Risk                15%
        Information Asymmetry      15%
        Quality Risk               15%
        Reliability Risk           15%

    Returns:
        Supplier-level risk analysis DataFrame.
    """

    # --------------------------------------------------------
    # Start with supplier analysis
    # --------------------------------------------------------

    result = supplier_analysis.copy()

    # --------------------------------------------------------
    # Delivery Performance
    # --------------------------------------------------------

    if delivery_kpis is not None and not delivery_kpis.empty:

        delivery_columns = [
            "supplier_id",
            "total_orders",
            "average_delay_days",
            "maximum_delay_days",
            "on_time_delivery_pct",
            "delivery_risk"
        ]

        available_columns = [
            column
            for column in delivery_columns
            if column in delivery_kpis.columns
        ]

        if "supplier_id" in available_columns:

            result = result.merge(
                delivery_kpis[available_columns],
                on="supplier_id",
                how="left"
            )

    # --------------------------------------------------------
    # Quotation Slippage
    # --------------------------------------------------------

    if quotation_kpis is not None and not quotation_kpis.empty:

        quotation_columns = [
            "supplier_id",
            "quotation_count",
            "average_price_slippage",
            "average_price_slippage_pct",
            "total_revisions",
            "average_validity_days",
            "quotation_slippage_risk"
        ]

        available_columns = [
            column
            for column in quotation_columns
            if column in quotation_kpis.columns
        ]

        if "supplier_id" in available_columns:

            result = result.merge(
                quotation_kpis[available_columns],
                on="supplier_id",
                how="left"
            )

    # --------------------------------------------------------
    # Timing Analysis
    # --------------------------------------------------------

    if timing_analysis is not None and not timing_analysis.empty:

        timing_columns = [
            "supplier_id",
            "timing_dependency",
            "timing_risk"
        ]

        available_columns = [
            column
            for column in timing_columns
            if column in timing_analysis.columns
        ]

        if "supplier_id" in available_columns:

            result = result.merge(
                timing_analysis[available_columns],
                on="supplier_id",
                how="left"
            )

    # --------------------------------------------------------
    # Information Asymmetry
    # --------------------------------------------------------

    if (
        information_asymmetry is not None
        and not information_asymmetry.empty
    ):

        information_columns = [
            "supplier_id",
            "information_asymmetry_score",
            "information_asymmetry_level"
        ]

        available_columns = [
            column
            for column in information_columns
            if column in information_asymmetry.columns
        ]

        if "supplier_id" in available_columns:

            result = result.merge(
                information_asymmetry[available_columns],
                on="supplier_id",
                how="left"
            )

    # ========================================================
    # DEFAULT VALUES
    # ========================================================

    if "delivery_risk" not in result.columns:
        result["delivery_risk"] = "Unknown"

    if "quotation_slippage_risk" not in result.columns:
        result["quotation_slippage_risk"] = "Unknown"

    if "timing_risk" not in result.columns:
        result["timing_risk"] = "Unknown"

    if "information_asymmetry_score" not in result.columns:
        result["information_asymmetry_score"] = 0.5

    if "information_asymmetry_level" not in result.columns:
        result["information_asymmetry_level"] = "Unknown"

    # ========================================================
    # DELIVERY RISK SCORE
    # Weight = 25%
    # ========================================================

    def calculate_delivery_risk(risk):

        if risk == "High":
            return 100

        if risk == "Medium":
            return 60

        if risk == "Low":
            return 20

        return 50

    result["delivery_risk_score"] = (
        result["delivery_risk"]
        .apply(calculate_delivery_risk)
    )

    # ========================================================
    # QUOTATION RISK SCORE
    # Weight = 15%
    # ========================================================

    def calculate_quotation_risk(risk):

        if risk == "High":
            return 100

        if risk == "Medium":
            return 60

        if risk == "Low":
            return 20

        return 50

    result["quotation_risk_score"] = (
        result["quotation_slippage_risk"]
        .apply(calculate_quotation_risk)
    )

    # ========================================================
    # TIMING RISK SCORE
    # Weight = 15%
    # ========================================================

    def calculate_timing_risk(risk):

        if risk == "High Timing Risk":
            return 100

        if risk == "Medium Timing Risk":
            return 60

        if risk == "Low Timing Risk":
            return 20

        return 50

    result["timing_risk_score"] = (
        result["timing_risk"]
        .apply(calculate_timing_risk)
    )

    # ========================================================
    # INFORMATION ASYMMETRY RISK
    # Weight = 15%
    # ========================================================

    result["information_asymmetry_score"] = pd.to_numeric(
        result["information_asymmetry_score"],
        errors="coerce"
    ).fillna(0.5)

    result["information_risk_score"] = (
        result["information_asymmetry_score"] * 100
    )

    # ========================================================
    # QUALITY RISK
    # Weight = 15%
    # ========================================================

    if "quality_score" in result.columns:

        result["quality_score"] = pd.to_numeric(
            result["quality_score"],
            errors="coerce"
        ).fillna(80)

        result["quality_risk_score"] = (
            100 - result["quality_score"]
        )

    else:

        result["quality_risk_score"] = 50

    # ========================================================
    # RELIABILITY RISK
    # Weight = 15%
    # ========================================================

    if "reliability_score" in result.columns:

        result["reliability_score"] = pd.to_numeric(
            result["reliability_score"],
            errors="coerce"
        ).fillna(80)

        result["reliability_risk_score"] = (
            100 - result["reliability_score"]
        )

    else:

        result["reliability_risk_score"] = 50

    # ========================================================
    # OVERALL RISK SCORE
    # ========================================================

    result["overall_risk_score"] = (
        result["delivery_risk_score"] * 0.25
        + result["quotation_risk_score"] * 0.15
        + result["timing_risk_score"] * 0.15
        + result["information_risk_score"] * 0.15
        + result["quality_risk_score"] * 0.15
        + result["reliability_risk_score"] * 0.15
    )

    result["overall_risk_score"] = (
        result["overall_risk_score"].round(2)
    )

    # ========================================================
    # OVERALL RISK LEVEL
    # ========================================================

    def classify_risk(score):

        if score >= 60:
            return "High"

        if score >= 30:
            return "Medium"

        return "Low"

    result["overall_risk_level"] = (
        result["overall_risk_score"]
        .apply(classify_risk)
    )

    # ========================================================
    # RISK RECOMMENDATION
    # ========================================================

    def generate_recommendation(row):

        recommendations = []

        # Delivery
        if row["delivery_risk"] == "High":
            recommendations.append(
                "Mitigate delivery risk"
            )

        elif row["delivery_risk"] == "Medium":
            recommendations.append(
                "Monitor delivery performance"
            )

        # Quotation
        if row["quotation_slippage_risk"] == "High":
            recommendations.append(
                "Strengthen quotation controls"
            )

        elif row["quotation_slippage_risk"] == "Medium":
            recommendations.append(
                "Monitor quotation changes"
            )

        # Timing
        if row["timing_risk"] == "High Timing Risk":
            recommendations.append(
                "Reduce timing dependency"
            )

        elif row["timing_risk"] == "Medium Timing Risk":
            recommendations.append(
                "Address timing dependency"
            )

        # Information asymmetry
        if row["information_asymmetry_level"] == "High":
            recommendations.append(
                "Verify supplier claims"
            )

        elif row["information_asymmetry_level"] == "Medium":
            recommendations.append(
                "Request additional evidence"
            )

        # Overall risk
        if row["overall_risk_level"] == "High":

            if recommendations:
                return (
                    "High Risk - "
                    + "; ".join(recommendations)
                )

            return (
                "High Risk - Enhanced supplier controls required"
            )

        if row["overall_risk_level"] == "Medium":

            if recommendations:
                return (
                    "Medium Risk - "
                    + "; ".join(recommendations)
                )

            return "Medium Risk - Monitor supplier"

        if recommendations:

            return (
                "Low Risk - "
                + "; ".join(recommendations)
            )

        return "Low Risk - Standard monitoring"

    result["risk_recommendation"] = result.apply(
        generate_recommendation,
        axis=1
    )

    # ========================================================
    # SORT BY RISK
    # ========================================================

    result = result.sort_values(
        by="overall_risk_score",
        ascending=False
    ).reset_index(drop=True)

    return result