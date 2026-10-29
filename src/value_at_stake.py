import pandas as pd


def calculate_value_at_stake(
    quotation_data,
    tco_summary=None,
    negotiation_case=None,
    batna_result=None
):
    """
    Calculate negotiation value-at-stake and potential savings.

    This model compares the supplier's current quoted price
    against the best available alternative cost.

    All monetary values are based on the supplied procurement
    dataset and should be treated as synthetic/sample values
    unless connected to validated enterprise data.
    """

    quotations = quotation_data.copy()

    # ---------------------------------------------------------
    # Normalize column names
    # ---------------------------------------------------------
    quotations.columns = [
        str(col).strip().lower()
        for col in quotations.columns
    ]

    # ---------------------------------------------------------
    # Required quotation fields
    # ---------------------------------------------------------
    required_columns = [
        "supplier_id",
        "material_id",
        "quantity",
        "initial_price"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in quotations.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Quotation data is missing required columns: {missing_columns}"
        )

    # ---------------------------------------------------------
    # Convert numeric fields
    # ---------------------------------------------------------
    quotations["quantity"] = pd.to_numeric(
        quotations["quantity"],
        errors="coerce"
    )

    quotations["initial_price"] = pd.to_numeric(
        quotations["initial_price"],
        errors="coerce"
    )

    quotations = quotations.dropna(
        subset=[
            "supplier_id",
            "material_id",
            "quantity",
            "initial_price"
        ]
    )

    # ---------------------------------------------------------
    # Determine alternative benchmark
    #
    # Preferred source:
    # TCO summary
    #
    # If TCO is unavailable:
    # use the lowest supplier quotation price.
    # ---------------------------------------------------------
    benchmark_source = "Quotation Price"

    if tco_summary is not None and not tco_summary.empty:

        tco = tco_summary.copy()

        tco.columns = [
            str(col).strip().lower()
            for col in tco.columns
        ]

        if (
            "supplier_id" in tco.columns
            and "tco_per_unit" in tco.columns
        ):

            tco["tco_per_unit"] = pd.to_numeric(
                tco["tco_per_unit"],
                errors="coerce"
            )

            tco = tco.dropna(
                subset=["supplier_id", "tco_per_unit"]
            )

            if not tco.empty:

                benchmark_cost = tco["tco_per_unit"].min()

                benchmark_supplier = tco.loc[
                    tco["tco_per_unit"].idxmin(),
                    "supplier_id"
                ]

                benchmark_source = "Best TCO Alternative"

            else:
                benchmark_cost = quotations[
                    "initial_price"
                ].min()

                benchmark_supplier = quotations.loc[
                    quotations["initial_price"].idxmin(),
                    "supplier_id"
                ]

        else:
            benchmark_cost = quotations[
                "initial_price"
            ].min()

            benchmark_supplier = quotations.loc[
                quotations["initial_price"].idxmin(),
                "supplier_id"
            ]

    else:

        benchmark_cost = quotations[
            "initial_price"
        ].min()

        benchmark_supplier = quotations.loc[
            quotations["initial_price"].idxmin(),
            "supplier_id"
        ]

    # ---------------------------------------------------------
    # Calculate value at stake for every supplier
    # ---------------------------------------------------------
    results = []

    for _, row in quotations.iterrows():

        supplier_id = row["supplier_id"]
        material_id = row["material_id"]
        quantity = float(row["quantity"])
        current_price = float(row["initial_price"])

        current_spend = current_price * quantity

        alternative_spend = benchmark_cost * quantity

        potential_savings = (
            current_spend - alternative_spend
        )

        savings_per_unit = (
            current_price - benchmark_cost
        )

        if current_spend != 0:
            savings_pct = (
                potential_savings / current_spend
            ) * 100
        else:
            savings_pct = 0.0

        # -----------------------------------------------------
        # Value-at-stake classification
        # -----------------------------------------------------
        if potential_savings <= 0:
            priority = "Low"
            opportunity = "No Immediate Savings"

        elif savings_pct >= 10:
            priority = "High"
            opportunity = "Significant Savings Opportunity"

        elif savings_pct >= 5:
            priority = "Medium"
            opportunity = "Moderate Savings Opportunity"

        else:
            priority = "Low"
            opportunity = "Limited Savings Opportunity"

        # -----------------------------------------------------
        # Recommendation
        # -----------------------------------------------------
        if potential_savings <= 0:

            recommendation = (
                "Current supplier price is at or below the "
                "best available benchmark. Focus on non-price "
                "negotiation levers."
            )

        elif priority == "High":

            recommendation = (
                "High value at stake. Use the alternative "
                "supplier benchmark to create negotiation "
                "pressure and target a significant price "
                "improvement."
            )

        elif priority == "Medium":

            recommendation = (
                "Moderate value at stake. Seek a measurable "
                "price reduction while protecting delivery, "
                "quality and commercial terms."
            )

        else:

            recommendation = (
                "Limited monetary opportunity. Focus on "
                "commercial terms, delivery, quality and "
                "relationship value."
            )

        results.append(
            {
                "supplier_id": supplier_id,
                "material_id": material_id,
                "quantity": quantity,
                "current_price_per_unit": current_price,
                "benchmark_price_per_unit": benchmark_cost,
                "benchmark_supplier": benchmark_supplier,
                "benchmark_source": benchmark_source,
                "current_spend": current_spend,
                "alternative_spend": alternative_spend,
                "potential_savings": potential_savings,
                "savings_per_unit": savings_per_unit,
                "savings_pct": savings_pct,
                "value_at_stake": max(potential_savings, 0),
                "negotiation_priority": priority,
                "opportunity": opportunity,
                "recommendation": recommendation
            }
        )

    result = pd.DataFrame(results)

    # ---------------------------------------------------------
    # Rank suppliers by value at stake
    # ---------------------------------------------------------
    if not result.empty:

        result = result.sort_values(
            by="value_at_stake",
            ascending=False
        ).reset_index(drop=True)

        result["value_at_stake_rank"] = (
            result["value_at_stake"]
            .rank(
                method="dense",
                ascending=False
            )
            .astype(int)
        )

    return result


def build_value_at_stake_summary(value_at_stake_result):
    """
    Build a supplier-level summary of negotiation opportunity.
    """

    if value_at_stake_result is None:
        return pd.DataFrame()

    if value_at_stake_result.empty:
        return pd.DataFrame()

    summary = (
        value_at_stake_result
        .groupby("supplier_id", as_index=False)
        .agg(
            total_current_spend=(
                "current_spend",
                "sum"
            ),
            total_alternative_spend=(
                "alternative_spend",
                "sum"
            ),
            total_value_at_stake=(
                "value_at_stake",
                "sum"
            ),
            average_savings_pct=(
                "savings_pct",
                "mean"
            ),
            maximum_savings_per_unit=(
                "savings_per_unit",
                "max"
            )
        )
    )

    summary["negotiation_priority"] = "Low"

    summary.loc[
        summary["total_value_at_stake"] > 0,
        "negotiation_priority"
    ] = "Medium"

    summary.loc[
        summary["average_savings_pct"] >= 10,
        "negotiation_priority"
    ] = "High"

    summary = summary.sort_values(
        by="total_value_at_stake",
        ascending=False
    ).reset_index(drop=True)

    summary["value_at_stake_rank"] = (
        summary["total_value_at_stake"]
        .rank(
            method="dense",
            ascending=False
        )
        .astype(int)
    )

    return summary


def calculate_complete_value_at_stake(
    quotation_data,
    tco_summary=None,
    negotiation_case=None,
    batna_result=None
):
    """
    Complete Value-at-Stake calculation.

    Returns:
        detail_result
        supplier_summary
    """

    detail_result = calculate_value_at_stake(
        quotation_data=quotation_data,
        tco_summary=tco_summary,
        negotiation_case=negotiation_case,
        batna_result=batna_result
    )

    supplier_summary = build_value_at_stake_summary(
        detail_result
    )

    return detail_result, supplier_summary


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("VALUE-AT-STAKE ANALYSIS")
    print("=" * 70)

    INPUT_FILE = (
        "data/input/Procurement_Negotiation_Input.xlsx"
    )

    quotation_data = pd.read_excel(
        INPUT_FILE,
        sheet_name="Quotation_Data"
    )

    tco_summary = pd.read_csv(
        "outputs/tco_supplier_summary.csv"
    )

    detail, summary = calculate_complete_value_at_stake(
        quotation_data=quotation_data,
        tco_summary=tco_summary
    )

    print("\nVALUE-AT-STAKE DETAIL")
    print("-" * 70)

    print(
        detail[
            [
                "supplier_id",
                "current_price_per_unit",
                "benchmark_price_per_unit",
                "potential_savings",
                "savings_per_unit",
                "savings_pct",
                "value_at_stake",
                "negotiation_priority"
            ]
        ].to_string(index=False)
    )

    print("\nSUPPLIER VALUE-AT-STAKE SUMMARY")
    print("-" * 70)

    print(
        summary.to_string(index=False)
    )

    print("\nValue-at-Stake analysis completed successfully.")