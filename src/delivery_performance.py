import pandas as pd


def analyze_delivery_performance(delivery_performance):

    result = delivery_performance.copy()

    # Convert dates
    result["promised_delivery_date"] = pd.to_datetime(
        result["promised_delivery_date"],
        errors="coerce"
    )

    result["actual_delivery_date"] = pd.to_datetime(
        result["actual_delivery_date"],
        errors="coerce"
    )

    # Convert numeric columns
    result["promised_days"] = pd.to_numeric(
        result["promised_days"],
        errors="coerce"
    )

    result["actual_days"] = pd.to_numeric(
        result["actual_days"],
        errors="coerce"
    )

    # Calculate delay
    result["delay_days"] = (
        result["actual_days"] - result["promised_days"]
    )

    # On-time delivery
    result["on_time"] = result["delay_days"] <= 0

    # Delay category
    def classify_delay(delay):

        if pd.isna(delay):
            return "Unknown"

        if delay <= 0:
            return "On Time"

        elif delay <= 2:
            return "Low Delay"

        elif delay <= 5:
            return "Moderate Delay"

        else:
            return "High Delay"

    result["delay_category"] = result["delay_days"].apply(
        classify_delay
    )

    return result


def calculate_supplier_delivery_kpis(delivery_performance):

    analysis = analyze_delivery_performance(
        delivery_performance
    )

    supplier_kpis = (
        analysis
        .groupby("supplier_id")
        .agg(
            total_orders=("po_id", "count"),
            average_delay_days=("delay_days", "mean"),
            maximum_delay_days=("delay_days", "max"),
            on_time_deliveries=("on_time", "sum")
        )
        .reset_index()
    )

    supplier_kpis["on_time_delivery_pct"] = (
        supplier_kpis["on_time_deliveries"]
        / supplier_kpis["total_orders"]
        * 100
    )

    def classify_risk(row):

        if row["on_time_delivery_pct"] >= 90:
            return "Low"

        elif row["on_time_delivery_pct"] >= 75:
            return "Medium"

        else:
            return "High"

    supplier_kpis["delivery_risk"] = supplier_kpis.apply(
        classify_risk,
        axis=1
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

    delivery_analysis = analyze_delivery_performance(
        delivery_performance
    )

    supplier_kpis = calculate_supplier_delivery_kpis(
        delivery_performance
    )

    print("\nDelivery Performance Analysis:")
    print(delivery_analysis)

    print("\nSupplier Delivery KPIs:")
    print(supplier_kpis)