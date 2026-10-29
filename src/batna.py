import pandas as pd

from src.supplier_analysis import analyze_suppliers
from src.outside_option import calculate_outside_options


# =========================================================
# BATNA CALCULATION
# =========================================================

def calculate_batna(
    supplier_data,
    purchase_history=None,
    quotation_data=None,
    negotiation_case=None,
    market_cost_data=None
):
    """
    Calculate the BATNA.

    BATNA is the feasible alternative supplier with the
    lowest effective outside-option cost.

    The function is designed for the main Excel-based
    procurement pipeline. All datasets should be supplied
    by main.py through data_loader.py.
    """

    # -----------------------------------------------------
    # Validate required datasets
    # -----------------------------------------------------

    if purchase_history is None:
        raise ValueError(
            "purchase_history is required for BATNA calculation."
        )

    if quotation_data is None:
        raise ValueError(
            "quotation_data is required for BATNA calculation."
        )

    if negotiation_case is None:
        raise ValueError(
            "negotiation_case is required for BATNA calculation."
        )

    if market_cost_data is None:
        raise ValueError(
            "market_cost_data is required for BATNA calculation."
        )

    # -----------------------------------------------------
    # Supplier analysis
    # -----------------------------------------------------

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    # -----------------------------------------------------
    # Required quantity
    # -----------------------------------------------------

    required_quantity = float(
        negotiation_case.iloc[0]["required_quantity"]
    )

    # -----------------------------------------------------
    # Outside-option analysis
    # -----------------------------------------------------

    outside_options = calculate_outside_options(
        supplier_analysis,
        market_cost_data,
        required_quantity
    )

    if outside_options.empty:
        return None

    # -----------------------------------------------------
    # Keep only feasible alternatives
    # -----------------------------------------------------

    if "supplier_id" in outside_options.columns:
        outside_options = outside_options[
            outside_options["supplier_id"].astype(str)
            != str(
                negotiation_case.iloc[0].get(
                    "current_supplier_id",
                    ""
                )
            )
        ].copy()

    # -----------------------------------------------------
    # Sort alternatives by effective cost
    # -----------------------------------------------------

    outside_options = outside_options.sort_values(
        by="effective_outside_option_cost",
        ascending=True
    ).reset_index(drop=True)

    if outside_options.empty:
        return None

    # -----------------------------------------------------
    # Best alternative = BATNA
    # -----------------------------------------------------

    batna_row = outside_options.iloc[0]

    batna = {
        "batna_supplier_id": batna_row["supplier_id"],
        "batna_supplier_name": batna_row["supplier_name"],
        "batna_cost": float(
            batna_row["effective_outside_option_cost"]
        )
    }

    return batna


# =========================================================
# BUILD BATNA COMPARISON
# =========================================================

def build_batna_comparison(
    supplier_data,
    purchase_history,
    quotation_data,
    negotiation_case,
    market_cost_data
):
    """
    Build the complete BATNA supplier comparison table.

    This function uses the datasets supplied by the main
    Excel-based pipeline and does not load CSV files.
    """

    # -----------------------------------------------------
    # Supplier analysis
    # -----------------------------------------------------

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    # -----------------------------------------------------
    # Required quantity
    # -----------------------------------------------------

    required_quantity = float(
        negotiation_case.iloc[0]["required_quantity"]
    )

    # -----------------------------------------------------
    # Outside options
    # -----------------------------------------------------

    comparison = calculate_outside_options(
        supplier_analysis,
        market_cost_data,
        required_quantity
    )

    if comparison.empty:
        return pd.DataFrame()

    # -----------------------------------------------------
    # Remove current supplier from BATNA alternatives
    # -----------------------------------------------------

    if "supplier_id" in comparison.columns:

        current_supplier = str(
            negotiation_case.iloc[0].get(
                "current_supplier_id",
                ""
            )
        ).strip()

        if current_supplier:
            comparison = comparison[
                comparison["supplier_id"]
                .astype(str)
                .str.strip()
                != current_supplier
            ].copy()

    if comparison.empty:
        return pd.DataFrame()

    # -----------------------------------------------------
    # Sort by effective outside-option cost
    # -----------------------------------------------------

    comparison = comparison.sort_values(
        by="effective_outside_option_cost",
        ascending=True
    ).reset_index(drop=True)

    comparison["rank"] = comparison.index + 1

    # -----------------------------------------------------
    # PRICE PER UNIT
    # -----------------------------------------------------

    if "initial_price" in comparison.columns:

        comparison["price_per_unit"] = pd.to_numeric(
            comparison["initial_price"],
            errors="coerce"
        )

    else:

        comparison["price_per_unit"] = pd.NA

        # Try quotation data if price is not already present

        if "supplier_id" in quotation_data.columns:

            quote_data = quotation_data.copy()

            quote_data.columns = (
                quote_data.columns
                .str.strip()
                .str.lower()
            )

            quote_data["supplier_id"] = (
                quote_data["supplier_id"]
                .astype(str)
                .str.strip()
            )

            case_rfq = str(
                negotiation_case.iloc[0]["rfq_id"]
            ).strip()

            case_material = str(
                negotiation_case.iloc[0]["material_id"]
            ).strip()

            if "rfq_id" in quote_data.columns:

                quote_data = quote_data[
                    quote_data["rfq_id"]
                    .astype(str)
                    .str.strip()
                    == case_rfq
                ]

            if "material_id" in quote_data.columns:

                quote_data = quote_data[
                    quote_data["material_id"]
                    .astype(str)
                    .str.strip()
                    == case_material
                ]

            if "initial_price" in quote_data.columns:

                quote_prices = (
                    quote_data[
                        [
                            "supplier_id",
                            "initial_price"
                        ]
                    ]
                    .drop_duplicates(
                        subset=["supplier_id"]
                    )
                )

                comparison = comparison.merge(
                    quote_prices,
                    on="supplier_id",
                    how="left"
                )

                comparison["price_per_unit"] = pd.to_numeric(
                    comparison["initial_price"],
                    errors="coerce"
                )

    # -----------------------------------------------------
    # Ensure price_per_unit exists
    # -----------------------------------------------------

    if "price_per_unit" not in comparison.columns:

        comparison["price_per_unit"] = pd.NA

    return comparison


# =========================================================
# DISPLAY BATNA COMPARISON
# =========================================================

def display_batna_comparison(
    supplier_data,
    purchase_history,
    quotation_data,
    negotiation_case,
    market_cost_data
):
    """
    Display the BATNA supplier comparison.
    """

    comparison = build_batna_comparison(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case,
        market_cost_data
    )

    if comparison.empty:

        print()
        print("=" * 100)
        print("                    BATNA SUPPLIER COMPARISON")
        print("=" * 100)
        print("No feasible alternative suppliers found.")
        print("=" * 100)

        return

    required_quantity = float(
        negotiation_case.iloc[0]["required_quantity"]
    )

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    print()
    print("=" * 120)
    print("                         BATNA SUPPLIER COMPARISON")
    print("=" * 120)

    if "case_id" in negotiation_case.columns:
        print(
            f"Case ID           : "
            f"{negotiation_case.iloc[0]['case_id']}"
        )

    if "rfq_id" in negotiation_case.columns:
        print(
            f"RFQ ID            : "
            f"{negotiation_case.iloc[0]['rfq_id']}"
        )

    if "material_id" in negotiation_case.columns:
        print(
            f"Material          : "
            f"{negotiation_case.iloc[0]['material_id']}"
        )

    print(
        f"Required Quantity : "
        f"{required_quantity:,.0f}"
    )

    print()

    # -----------------------------------------------------
    # CREATE DISPLAY TABLE
    # -----------------------------------------------------

    table = pd.DataFrame()

    table["Rank"] = comparison["rank"]

    table["Supplier ID"] = comparison["supplier_id"]

    table["Supplier Name"] = comparison["supplier_name"]

    table["Price / Unit"] = comparison["price_per_unit"]

    table["Base Cost"] = comparison["base_cost"]

    table["Switching Cost"] = comparison["switching_cost"]

    table["Effective Cost"] = (
        comparison["effective_outside_option_cost"]
    )

    if "supplier_score" in comparison.columns:

        table["Supplier Score"] = (
            comparison["supplier_score"]
        )

    # -----------------------------------------------------
    # FORMAT CURRENCY
    # -----------------------------------------------------

    currency_columns = [
        "Price / Unit",
        "Base Cost",
        "Switching Cost",
        "Effective Cost"
    ]

    for column in currency_columns:

        if column in table.columns:

            table[column] = table[column].apply(
                lambda value:
                f"₹{float(value):,.2f}"
                if pd.notna(value)
                else "-"
            )

    # -----------------------------------------------------
    # FORMAT SCORE
    # -----------------------------------------------------

    if "Supplier Score" in table.columns:

        table["Supplier Score"] = (
            table["Supplier Score"]
            .apply(
                lambda value:
                f"{float(value):.3f}"
                if pd.notna(value)
                else "-"
            )
        )

    # -----------------------------------------------------
    # PRINT COMPARISON
    # -----------------------------------------------------

    print(
        table.to_string(index=False)
    )

    # -----------------------------------------------------
    # BATNA RESULT
    # -----------------------------------------------------

    batna_row = comparison.iloc[0]

    batna_supplier = batna_row["supplier_name"]

    batna_supplier_id = batna_row["supplier_id"]

    batna_cost = float(
        batna_row["effective_outside_option_cost"]
    )

    batna_cost_per_unit = (
        batna_cost / required_quantity
        if required_quantity != 0
        else 0
    )

    # -----------------------------------------------------
    # FINAL BATNA
    # -----------------------------------------------------

    print()

    print("=" * 120)
    print("                              BATNA RESULT")
    print("=" * 120)

    print(
        f"BATNA Supplier      : {batna_supplier}"
    )

    print(
        f"BATNA Supplier ID   : {batna_supplier_id}"
    )

    print(
        f"BATNA Effective Cost: ₹{batna_cost:,.2f}"
    )

    print(
        f"BATNA Cost / Unit   : ₹{batna_cost_per_unit:,.2f}"
    )

    print()

    print(
        "Selection Rule:"
    )

    print(
        "BATNA = feasible alternative supplier "
        "with the lowest effective outside-option cost."
    )

    print("=" * 120)
    print()


# =========================================================
# STANDALONE EXECUTION
# =========================================================

if __name__ == "__main__":

    print()
    print(
        "BATNA module is designed to be called from main.py "
        "with the Excel-loaded datasets."
    )
    print()