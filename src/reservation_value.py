import pandas as pd


# ============================================================
# RESERVATION VALUE CALCULATION
# ============================================================

def calculate_reservation_value(batna):
    """
    Calculate the buyer's reservation value.

    Prototype assumption:
    Reservation Value = BATNA Effective Cost
    """

    reservation_value = batna["batna_cost"]

    return reservation_value


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
    # Import previous analysis modules
    # --------------------------------------------------------

    from supplier_analysis import analyze_suppliers
    from outside_option import calculate_outside_options
    from batna import calculate_batna

    # --------------------------------------------------------
    # Supplier Analysis
    # --------------------------------------------------------

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    print("Supplier analysis completed.")

    # --------------------------------------------------------
    # Required Quantity
    # --------------------------------------------------------

    required_quantity = negotiation_case.iloc[0][
        "required_quantity"
    ]

    # --------------------------------------------------------
    # Outside Option Analysis
    # --------------------------------------------------------

    outside_options = calculate_outside_options(
        supplier_analysis,
        market_cost_data,
        required_quantity
    )

    print("Outside-option analysis completed.")

    # --------------------------------------------------------
    # BATNA
    # --------------------------------------------------------

    batna = calculate_batna(
        outside_options
    )

    print("BATNA calculation completed.")

    # --------------------------------------------------------
    # Reservation Value
    # --------------------------------------------------------

    reservation_value = calculate_reservation_value(
        batna
    )

    # --------------------------------------------------------
    # Display Result
    # --------------------------------------------------------

    print("\n========================================")
    print(" RESERVATION VALUE ANALYSIS")
    print("========================================\n")

    print(
        f"BATNA Supplier       : "
        f"{batna['supplier_name']}"
    )

    print(
        f"BATNA Supplier ID    : "
        f"{batna['supplier_id']}"
    )

    print(
        f"BATNA Effective Cost : "
        f"₹{batna['batna_cost']:,.2f}"
    )

    print(
        f"Buyer Reservation Value : "
        f"₹{reservation_value:,.2f}"
    )

    print(
        "\nReservation value calculation "
        "completed successfully."
    )