import pandas as pd

INPUT_FILE = "data/input/Procurement_Negotiation_Input.xlsx"


def load_procurement_data():

    # Existing datasets
    supplier_data = pd.read_excel(
        INPUT_FILE,
        sheet_name="Supplier_Data"
    )

    purchase_history = pd.read_excel(
        INPUT_FILE,
        sheet_name="Purchase_History"
    )

    quotation_data = pd.read_excel(
        INPUT_FILE,
        sheet_name="Quotation_Data"
    )

    negotiation_history = pd.read_excel(
        INPUT_FILE,
        sheet_name="Negotiation_History"
    )

    market_cost_data = pd.read_excel(
        INPUT_FILE,
        sheet_name="Market_Cost_Data"
    )

    negotiation_case = pd.read_excel(
        INPUT_FILE,
        sheet_name="Negotiation_Case"
    )

    supplier_signals = pd.read_excel(
        INPUT_FILE,
        sheet_name="Supplier_Signals"
    )

    # New datasets
    supplier_location = pd.read_excel(
        INPUT_FILE,
        sheet_name="Supplier_Location"
    )

    delivery_performance = pd.read_excel(
        INPUT_FILE,
        sheet_name="Delivery_Performance"
    )

    quotation_slippage = pd.read_excel(
        INPUT_FILE,
        sheet_name="Quotation_Slippage"
    )

    supplier_timeline = pd.read_excel(
        INPUT_FILE,
        sheet_name="Supplier_Timeline"
    )

    print("All 11 procurement datasets loaded successfully!")

    return (
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
    )


if __name__ == "__main__":

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

    print("\nSupplier Data:")
    print(supplier_data)

    print("\nPurchase History:")
    print(purchase_history)

    print("\nQuotation Data:")
    print(quotation_data)

    print("\nNegotiation History:")
    print(negotiation_history)

    print("\nMarket Cost Data:")
    print(market_cost_data)

    print("\nNegotiation Case:")
    print(negotiation_case)

    print("\nSupplier Signals:")
    print(supplier_signals)

    print("\nSupplier Location:")
    print(supplier_location)

    print("\nDelivery Performance:")
    print(delivery_performance)

    print("\nQuotation Slippage:")
    print(quotation_slippage)

    print("\nSupplier Timeline:")
    print(supplier_timeline)