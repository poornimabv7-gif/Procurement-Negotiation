import pandas as pd


# ============================================================
# NASH BARGAINING CALCULATION
# ============================================================

def calculate_nash_bargaining(
    supplier_analysis,
    purchase_history,
    negotiation_case,
    buyer_reservation_value
):
    """
    Calculate a prototype Nash bargaining solution.

    Assumptions:
    - Only feasible suppliers are considered.
    - Supplier reservation price is approximated by
      the supplier's historical average purchase price.
    - Buyer reservation price is the buyer's reservation value.
    - Equal bargaining power is assumed.
    - Utilities are assumed to be linear in price.

    Prototype model:
        Nash Price =
        (Supplier Reservation Price
         + Buyer Reservation Price) / 2

    IMPORTANT:
    Historical average purchase price is a proxy for
    supplier reservation price. It is NOT the supplier's
    actual minimum acceptable price.
    """

    # --------------------------------------------------------
    # Copy supplier analysis
    # --------------------------------------------------------

    supplier_analysis = supplier_analysis.copy()

    # --------------------------------------------------------
    # Create feasibility flag
    # --------------------------------------------------------

    supplier_analysis["feasible"] = (
        supplier_analysis["capacity_feasible"]
        & supplier_analysis["delivery_feasible"]
        & supplier_analysis["qualified"]
    )

    # --------------------------------------------------------
    # Keep only feasible suppliers
    # --------------------------------------------------------

    feasible_suppliers = supplier_analysis[
        supplier_analysis["feasible"] == True
    ].copy()

    # --------------------------------------------------------
    # Calculate historical average price by supplier
    # --------------------------------------------------------

    historical_prices = (
        purchase_history
        .groupby("supplier_id")["purchase_price"]
        .mean()
        .reset_index()
    )

    historical_prices = historical_prices.rename(
        columns={
            "purchase_price": "historical_avg_price"
        }
    )

    # --------------------------------------------------------
    # Add historical average price to supplier analysis
    # --------------------------------------------------------

    feasible_suppliers = feasible_suppliers.merge(
        historical_prices,
        on="supplier_id",
        how="left"
    )

    # --------------------------------------------------------
    # Required quantity
    # --------------------------------------------------------

    required_quantity = negotiation_case.iloc[0][
        "required_quantity"
    ]

    # --------------------------------------------------------
    # Buyer reservation price per unit
    # --------------------------------------------------------

    buyer_reservation_per_unit = (
        buyer_reservation_value
        / required_quantity
    )

    results = []

    # --------------------------------------------------------
    # Calculate Nash bargaining solution
    # --------------------------------------------------------

    for _, supplier in feasible_suppliers.iterrows():

        # Skip suppliers without historical pricing data
        if pd.isna(
            supplier["historical_avg_price"]
        ):
            continue

        supplier_reservation_per_unit = (
            supplier["historical_avg_price"]
        )

        # Equal bargaining power assumption
        nash_price_per_unit = (
            supplier_reservation_per_unit
            + buyer_reservation_per_unit
        ) / 2

        # Convert to total negotiation value
        nash_total_price = (
            nash_price_per_unit
            * required_quantity
        )

        results.append({

            "supplier_id":
                supplier["supplier_id"],

            "supplier_name":
                supplier["supplier_name"],

            "historical_avg_price":
                supplier_reservation_per_unit,

            "supplier_reservation_per_unit":
                supplier_reservation_per_unit,

            "buyer_reservation_per_unit":
                buyer_reservation_per_unit,

            "nash_price_per_unit":
                nash_price_per_unit,

            "nash_total_price":
                nash_total_price
        })

    return pd.DataFrame(results)


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("\nLoading procurement datasets...\n")

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

    # --------------------------------------------------------
    # Import previous modules
    # --------------------------------------------------------

    from supplier_analysis import analyze_suppliers

    from outside_option import (
        calculate_outside_options
    )

    from batna import calculate_batna

    from reservation_value import (
        calculate_reservation_value
    )

    # --------------------------------------------------------
    # 1. Supplier Analysis
    # --------------------------------------------------------

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    print("Supplier analysis completed.")

    # --------------------------------------------------------
    # 2. Required quantity
    # --------------------------------------------------------

    required_quantity = negotiation_case.iloc[0][
        "required_quantity"
    ]

    # --------------------------------------------------------
    # 3. Outside Options
    # --------------------------------------------------------

    outside_options = calculate_outside_options(
        supplier_analysis,
        market_cost_data,
        required_quantity
    )

    print("Outside-option analysis completed.")

    # --------------------------------------------------------
    # 4. BATNA
    # --------------------------------------------------------

    batna = calculate_batna(
        outside_options
    )

    print("BATNA calculation completed.")

    # --------------------------------------------------------
    # 5. Reservation Value
    # --------------------------------------------------------

    buyer_reservation_value = (
        calculate_reservation_value(batna)
    )

    print("Reservation value calculation completed.")

    # --------------------------------------------------------
    # 6. Nash Bargaining
    # --------------------------------------------------------

    nash_result = calculate_nash_bargaining(
        supplier_analysis,
        purchase_history,
        negotiation_case,
        buyer_reservation_value
    )

    # --------------------------------------------------------
    # Display Results
    # --------------------------------------------------------

    print("\n========================================")
    print(" NASH BARGAINING ANALYSIS")
    print("========================================\n")

    if nash_result.empty:

        print(
            "No feasible suppliers with historical "
            "pricing available for Nash analysis."
        )

    else:

        print(
            nash_result.to_string(index=False)
        )

    print(
        "\nNash bargaining calculation "
        "completed successfully."
    )