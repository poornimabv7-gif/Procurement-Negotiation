import pandas as pd


def calculate_market_benchmark(market_cost_data):
    """
    Calculate a market-based should-cost benchmark.

    Current dataset:
        material_id
        date
        commodity_price
        market_price
        transport_cost

    For the current prototype, the delivered market benchmark is:

        market_price + transport_cost

    The latest available observation is used as the
    operational should-cost benchmark.
    """

    data = market_cost_data.copy()

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    required_columns = [
        "material_id",
        "date",
        "commodity_price",
        "market_price",
        "transport_cost"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Market_Cost_Data is missing required columns: "
            + ", ".join(missing_columns)
        )

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    numeric_columns = [
        "commodity_price",
        "market_price",
        "transport_cost"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna(
        subset=[
            "material_id",
            "date",
            "commodity_price",
            "market_price",
            "transport_cost"
        ]
    ).copy()

    # Delivered market benchmark
    data["delivered_market_cost"] = (
        data["market_price"]
        + data["transport_cost"]
    )

    # Historical averages
    historical = (
        data.groupby("material_id")
        .agg(
            average_commodity_price=(
                "commodity_price",
                "mean"
            ),
            average_market_price=(
                "market_price",
                "mean"
            ),
            average_transport_cost=(
                "transport_cost",
                "mean"
            ),
            average_delivered_market_cost=(
                "delivered_market_cost",
                "mean"
            ),
            market_observation_count=(
                "delivered_market_cost",
                "count"
            ),
            latest_market_date=(
                "date",
                "max"
            )
        )
        .reset_index()
    )

    # Latest available market observation
    latest = (
        data.sort_values("date")
        .groupby("material_id")
        .tail(1)
        [
            [
                "material_id",
                "date",
                "commodity_price",
                "market_price",
                "transport_cost",
                "delivered_market_cost"
            ]
        ]
        .rename(
            columns={
                "date": "latest_market_date_actual",
                "commodity_price": "latest_commodity_price",
                "market_price": "latest_market_price",
                "transport_cost": "latest_transport_cost",
                "delivered_market_cost": "latest_delivered_market_cost"
            }
        )
    )

    benchmark = historical.merge(
        latest,
        on="material_id",
        how="left"
    )

    # Operational should-cost benchmark
    benchmark["should_cost"] = (
        benchmark["latest_delivered_market_cost"]
    )

    return benchmark


def calculate_supplier_should_cost(
    market_cost_data,
    quotation_data
):
    """
    Compare supplier quotations against
    the market-based should-cost benchmark.
    """

    benchmark = calculate_market_benchmark(
        market_cost_data
    )

    quotations = quotation_data.copy()

    quotations.columns = [
        str(column).strip()
        for column in quotations.columns
    ]

    required_columns = [
        "rfq_id",
        "supplier_id",
        "material_id",
        "quantity",
        "initial_price"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in quotations.columns
    ]

    if missing_columns:
        raise ValueError(
            "Quotation_Data is missing required columns: "
            + ", ".join(missing_columns)
        )

    quotations["initial_price"] = pd.to_numeric(
        quotations["initial_price"],
        errors="coerce"
    )

    quotations["quantity"] = pd.to_numeric(
        quotations["quantity"],
        errors="coerce"
    )

    result = quotations.merge(
        benchmark,
        on="material_id",
        how="left"
    )

    # Supplier quote compared with should-cost
    result["price_gap"] = (
        result["initial_price"]
        - result["should_cost"]
    )

    result["price_gap_pct"] = (
        result["price_gap"]
        / result["should_cost"]
    ) * 100

    def classify_cost_position(gap_pct):

        if pd.isna(gap_pct):
            return "Insufficient Data"

        if gap_pct <= 0:
            return "Below / At Should-Cost"

        if gap_pct <= 5:
            return "Highly Competitive"

        if gap_pct <= 10:
            return "Competitive"

        if gap_pct <= 20:
            return "Above Benchmark"

        return "Significantly Above Benchmark"

    result["cost_position"] = (
        result["price_gap_pct"]
        .apply(classify_cost_position)
    )

    def generate_recommendation(row):

        position = row["cost_position"]

        if position == "Below / At Should-Cost":
            return (
                "Price is at or below the market-based "
                "should-cost benchmark. Validate quality, "
                "capacity and commercial sustainability."
            )

        if position == "Highly Competitive":
            return (
                "Price is close to should-cost. "
                "Use targeted negotiation rather than "
                "aggressive price pressure."
            )

        if position == "Competitive":
            return (
                "Price is moderately above should-cost. "
                "Seek a reasonable commercial improvement."
            )

        if position == "Above Benchmark":
            return (
                "Price is above the should-cost benchmark. "
                "Challenge supplier cost assumptions and "
                "seek price improvement."
            )

        if position == "Significantly Above Benchmark":
            return (
                "Price is significantly above the should-cost "
                "benchmark. Conduct a detailed cost challenge "
                "and use available negotiation leverage."
            )

        return "Insufficient market cost evidence."

    result["should_cost_recommendation"] = result.apply(
        generate_recommendation,
        axis=1
    )

    return result


def calculate_should_cost(
    market_cost_data,
    quotation_data
):
    """
    Main public function for the Should-Cost module.
    """

    return calculate_supplier_should_cost(
        market_cost_data,
        quotation_data
    )


if __name__ == "__main__":

    print("=" * 70)
    print("SHOULD-COST MODEL TEST")
    print("=" * 70)

    input_file = (
        "data/input/"
        "Procurement_Negotiation_Input.xlsx"
    )

    market_cost_data = pd.read_excel(
        input_file,
        sheet_name="Market_Cost_Data"
    )

    quotation_data = pd.read_excel(
        input_file,
        sheet_name="Quotation_Data"
    )

    print()
    print("Market Cost Data:")
    print(
        market_cost_data.to_string(
            index=False
        )
    )

    print()
    print("Quotation Data:")
    print(
        quotation_data.to_string(
            index=False
        )
    )

    print()
    print("Running Should-Cost Analysis...")

    should_cost_analysis = calculate_should_cost(
        market_cost_data,
        quotation_data
    )

    print()
    print("===== MARKET SHOULD-COST BENCHMARK =====")

    benchmark_columns = [
        "material_id",
        "average_commodity_price",
        "average_market_price",
        "average_transport_cost",
        "average_delivered_market_cost",
        "latest_commodity_price",
        "latest_market_price",
        "latest_transport_cost",
        "latest_delivered_market_cost",
        "should_cost",
        "market_observation_count"
    ]

    print(
        should_cost_analysis[
            benchmark_columns
        ]
        .drop_duplicates()
        .to_string(index=False)
    )

    print()
    print("===== SUPPLIER SHOULD-COST ANALYSIS =====")

    result_columns = [
        "supplier_id",
        "material_id",
        "initial_price",
        "should_cost",
        "price_gap",
        "price_gap_pct",
        "cost_position",
        "should_cost_recommendation"
    ]

    print(
        should_cost_analysis[
            result_columns
        ].to_string(index=False)
    )

    print()
    print("=" * 70)
    print("SHOULD-COST MODEL TEST COMPLETED")
    print("=" * 70)