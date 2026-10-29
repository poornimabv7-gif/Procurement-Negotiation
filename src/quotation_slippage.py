import pandas as pd


def analyze_quotation_slippage(quotation_slippage):

    result = quotation_slippage.copy()

    # Convert dates
    result["quotation_date"] = pd.to_datetime(
        result["quotation_date"],
        errors="coerce"
    )

    result["quoted_valid_until"] = pd.to_datetime(
        result["quoted_valid_until"],
        errors="coerce"
    )

    # Convert prices
    result["original_price"] = pd.to_numeric(
        result["original_price"],
        errors="coerce"
    )

    result["revised_price"] = pd.to_numeric(
        result["revised_price"],
        errors="coerce"
    )

    result["revision_count"] = pd.to_numeric(
        result["revision_count"],
        errors="coerce"
    )

    # Calculate price slippage
    result["price_slippage"] = (
        result["revised_price"]
        -
        result["original_price"]
    )

    # Calculate percentage slippage
    result["price_slippage_pct"] = (
        result["price_slippage"]
        /
        result["original_price"]
        *
        100
    )

    # Calculate quotation validity period
    result["quotation_validity_days"] = (
        result["quoted_valid_until"]
        -
        result["quotation_date"]
    ).dt.days

    # Classify quotation behaviour
    def classify_slippage(value):

        if pd.isna(value):
            return "Unknown"

        if value <= 0:
            return "No Slippage"

        elif value <= 2:
            return "Low Slippage"

        elif value <= 5:
            return "Moderate Slippage"

        else:
            return "High Slippage"

    result["slippage_risk"] = (
        result["price_slippage_pct"]
        .apply(classify_slippage)
    )

    return result


def calculate_quotation_slippage_kpis(
    quotation_slippage
):

    analysis = analyze_quotation_slippage(
        quotation_slippage
    )

    supplier_kpis = (
        analysis
        .groupby("supplier_id")
        .agg(
            quotation_count=(
                "supplier_id",
                "count"
            ),

            average_price_slippage=(
                "price_slippage",
                "mean"
            ),

            average_price_slippage_pct=(
                "price_slippage_pct",
                "mean"
            ),

            total_revisions=(
                "revision_count",
                "sum"
            ),

            average_validity_days=(
                "quotation_validity_days",
                "mean"
            )
        )
        .reset_index()
    )

    def classify_supplier_risk(value):

        if pd.isna(value):
            return "Unknown"

        if value <= 0:
            return "Low"

        elif value <= 2:
            return "Low"

        elif value <= 5:
            return "Medium"

        else:
            return "High"

    supplier_kpis["quotation_slippage_risk"] = (
        supplier_kpis[
            "average_price_slippage_pct"
        ]
        .apply(classify_supplier_risk)
    )

    return supplier_kpis


if __name__ == "__main__":

    from data_loader import load_procurement_data

    (
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_history,
        market_cost_data,
        negotiation_case,
        supplier_signals,
        supplier_location,
        delivery_performance,
        quotation_slippage,
        supplier_timeline
    ) = load_procurement_data()

    quotation_analysis = analyze_quotation_slippage(
        quotation_slippage
    )

    quotation_kpis = (
        calculate_quotation_slippage_kpis(
            quotation_slippage
        )
    )

    print("\nQuotation Slippage Analysis:")
    print(quotation_analysis)

    print("\nSupplier Quotation KPIs:")
    print(quotation_kpis)