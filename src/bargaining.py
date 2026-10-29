import pandas as pd


def calculate_zopa_for_bargaining(
    quotation_data,
    negotiation_case,
    buyer_reservation_value
):
    """
    Calculate the ZOPA information required by the
    bargaining analysis.

    Buyer reservation value is the maximum total amount
    the buyer is willing to pay.
    """

    required_quantity = negotiation_case.iloc[0]["required_quantity"]

    zopa = quotation_data.copy()

    # Supplier's quoted total price
    zopa["supplier_price_total"] = (
        zopa["initial_price"] * required_quantity
    )

    # Buyer reservation value
    zopa["buyer_reservation_value"] = buyer_reservation_value

    # Check whether supplier price is within buyer's
    # acceptable range
    zopa["zopa_exists"] = (
        zopa["supplier_price_total"]
        <= buyer_reservation_value
    )

    # Lower and upper boundaries
    zopa["zopa_low"] = zopa.apply(
        lambda row:
            row["supplier_price_total"]
            if row["zopa_exists"]
            else float("nan"),
        axis=1
    )

    zopa["zopa_high"] = zopa.apply(
        lambda row:
            buyer_reservation_value
            if row["zopa_exists"]
            else float("nan"),
        axis=1
    )

    return zopa[
        [
            "supplier_id",
            "supplier_price_total",
            "buyer_reservation_value",
            "zopa_exists",
            "zopa_low",
            "zopa_high"
        ]
    ]


def analyze_bargaining(
    nash_result,
    zopa_result
):
    """
    Interpret Nash bargaining results together with ZOPA.
    """

    result = nash_result.copy()

    # Add ZOPA information
    result = result.merge(
        zopa_result[
            [
                "supplier_id",
                "zopa_exists",
                "zopa_low",
                "zopa_high"
            ]
        ],
        on="supplier_id",
        how="left"
    )

    # Check whether Nash price is within buyer reservation
    result["within_buyer_reservation"] = (
        result["nash_price_per_unit"]
        <= result["buyer_reservation_per_unit"]
    )

    def determine_position(row):

        if not row["zopa_exists"]:
            return "No ZOPA - Review Negotiation"

        if row["within_buyer_reservation"]:
            return "Bargaining Feasible"

        return "Above Buyer Reservation"

    result["negotiation_position"] = (
        result.apply(
            determine_position,
            axis=1
        )
    )

    # Difference between supplier reservation
    # and Nash bargaining reference
    result["nash_vs_supplier_gap"] = (
        result["supplier_reservation_per_unit"]
        - result["nash_price_per_unit"]
    )

    return result


if __name__ == "__main__":

    # ==================================================
    # LOAD DATA
    # ==================================================

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

    # ==================================================
    # IMPORT PREVIOUS MODULES
    # ==================================================

    from supplier_analysis import analyze_suppliers
    from outside_option import calculate_outside_options
    from batna import calculate_batna
    from reservation_value import calculate_reservation_value
    from nash_bargaining import calculate_nash_bargaining

    # ==================================================
    # SUPPLIER ANALYSIS
    # ==================================================

    supplier_analysis = analyze_suppliers(
        supplier_data,
        quotation_data,
        purchase_history,
        negotiation_case
    )

    # ==================================================
    # REQUIRED QUANTITY
    # ==================================================

    required_quantity = negotiation_case.iloc[0][
        "required_quantity"
    ]

    # ==================================================
    # OUTSIDE OPTION
    # ==================================================

    outside_options = calculate_outside_options(
        supplier_analysis,
        market_cost_data,
        required_quantity
    )

    # ==================================================
    # BATNA
    # ==================================================

    batna = calculate_batna(
        outside_options
    )

    # ==================================================
    # BUYER RESERVATION VALUE
    # ==================================================

    buyer_reservation_value = (
        calculate_reservation_value(batna)
    )

    # ==================================================
    # ZOPA
    # ==================================================

    zopa_result = calculate_zopa_for_bargaining(
        quotation_data,
        negotiation_case,
        buyer_reservation_value
    )

    # ==================================================
    # NASH BARGAINING
    # ==================================================

    nash_result = calculate_nash_bargaining(
        supplier_analysis,
        negotiation_case,
        buyer_reservation_value
    )

    # ==================================================
    # BARGAINING ANALYSIS
    # ==================================================

    bargaining_result = analyze_bargaining(
        nash_result,
        zopa_result
    )

    # ==================================================
    # DISPLAY RESULT
    # ==================================================

    print("\n===== BARGAINING ANALYSIS =====\n")

    if bargaining_result.empty:

        print(
            "No suppliers available for "
            "bargaining analysis."
        )

    else:

        print(
            bargaining_result[
                [
                    "supplier_id",
                    "supplier_name",
                    "supplier_reservation_per_unit",
                    "buyer_reservation_per_unit",
                    "nash_price_per_unit",
                    "zopa_exists",
                    "zopa_low",
                    "zopa_high",
                    "within_buyer_reservation",
                    "negotiation_position"
                ]
            ].to_string(index=False)
        )