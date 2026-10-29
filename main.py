import os
import inspect
import pandas as pd


# ============================================================
# PROJECT MODULES
# ============================================================

from src.data_loader import load_procurement_data

from src.delivery_performance import (
    analyze_delivery_performance,
    calculate_supplier_delivery_kpis
)

from src.quotation_slippage import (
    analyze_quotation_slippage,
    calculate_quotation_slippage_kpis
)

from src.supplier_analysis import analyze_suppliers
from src.outside_option import calculate_outside_options
from src.reservation_value import calculate_reservation_value
from src.nash_bargaining import calculate_nash_bargaining
from src.zopa import calculate_zopa

from src.signalling import analyze_signals
from src.credibility import assess_credibility

from src.outside_option_verification import (
    verify_outside_option_signals
)

from src.information_asymmetry import (
    analyze_information_asymmetry
)

from src.timing_model import analyze_timing
from src.supplier_risk import calculate_supplier_risk
from src.supplier_timeline import calculate_supplier_timeline

from src.should_cost import calculate_should_cost
from src.tco_model import calculate_complete_tco
from src.value_at_stake import calculate_complete_value_at_stake

from src.shapley import calculate_shapley_values

from src.negotiation_decision import (
    build_negotiation_decision
)

from src.negotiation_strategy import (
    build_negotiation_strategy
)

from src.negotiation_brief import (
    build_negotiation_brief
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_PATH,
    exist_ok=True
)


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_csv(data, filename):

    path = os.path.join(
        OUTPUT_PATH,
        filename
    )

    if isinstance(data, pd.Series):
        data = data.to_frame()

    elif isinstance(data, dict):
        data = pd.DataFrame([data])

    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    data.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"   ✓ Saved: outputs/{filename}"
    )

    return path


# ============================================================
# FINAL REPORT GENERATION
# ============================================================

def generate_final_html_report(report_data):
    """
    Generate the final HTML report using src.final_report.

    This function is deliberately compatible with both possible
    function names:

        generate_final_report(...)
        generate_report(...)

    It also adapts to the function's actual parameters so that
    main.py does not fail simply because the report module uses
    a different function signature.
    """

    try:

        from src import final_report

    except Exception as exc:

        print()
        print(
            "   ✗ Could not import src.final_report"
        )
        print(
            f"   Error: {exc}"
        )
        return False

    # --------------------------------------------------------
    # Find the available report-generation function
    # --------------------------------------------------------

    report_function = None

    if hasattr(
        final_report,
        "generate_final_report"
    ):

        report_function = (
            final_report.generate_final_report
        )

    elif hasattr(
        final_report,
        "generate_report"
    ):

        report_function = (
            final_report.generate_report
        )

    if report_function is None:

        print()
        print(
            "   ✗ No report generation function found."
        )

        print(
            "   Expected one of:"
        )

        print(
            "      generate_final_report"
        )

        print(
            "      generate_report"
        )

        return False

    # --------------------------------------------------------
    # Prepare possible arguments
    # --------------------------------------------------------

    output_file = os.path.join(
        OUTPUT_PATH,
        "final_negotiation_report.html"
    )

    available_data = {

        # Main analytical results
        "final_decision_result":
            report_data.get(
                "final_decision_result"
            ),

        "negotiation_strategy_result":
            report_data.get(
                "negotiation_strategy_result"
            ),

        "negotiation_brief_result":
            report_data.get(
                "negotiation_brief_result"
            ),

        "negotiation_brief_summary":
            report_data.get(
                "negotiation_brief_summary"
            ),

        "strategy_result":
            report_data.get(
                "negotiation_strategy_result"
            ),

        # Core negotiation models
        "zopa_result":
            report_data.get(
                "zopa_result"
            ),

        "nash_result":
            report_data.get(
                "nash_result"
            ),

        "reservation_result":
            report_data.get(
                "reservation_result"
            ),

        "batna_result":
            report_data.get(
                "batna_result"
            ),

        "batna":
            report_data.get(
                "batna"
            ),

        # Cost analysis
        "should_cost_result":
            report_data.get(
                "should_cost_result"
            ),

        "tco_summary":
            report_data.get(
                "tco_summary"
            ),

        "tco_detail":
            report_data.get(
                "tco_detail"
            ),

        "value_at_stake_summary":
            report_data.get(
                "value_at_stake_summary"
            ),

        "value_at_stake_detail":
            report_data.get(
                "value_at_stake_detail"
            ),

        # Game theory
        "shapley_result":
            report_data.get(
                "shapley_result"
            ),

        "shapley_total":
            report_data.get(
                "shapley_total"
            ),

        # Supplier analytics
        "supplier_analysis":
            report_data.get(
                "supplier_analysis"
            ),

        "supplier_risk_result":
            report_data.get(
                "supplier_risk_result"
            ),

        "supplier_timeline_result":
            report_data.get(
                "supplier_timeline_result"
            ),

        "delivery_kpis":
            report_data.get(
                "delivery_kpis"
            ),

        "quotation_slippage_kpis":
            report_data.get(
                "quotation_slippage_kpis"
            ),

        "timing_result":
            report_data.get(
                "timing_result"
            ),

        "information_result":
            report_data.get(
                "information_result"
            ),

        "credibility_result":
            report_data.get(
                "credibility_result"
            ),

        "verification_result":
            report_data.get(
                "verification_result"
            ),

        # Raw input
        "negotiation_case":
            report_data.get(
                "negotiation_case"
            ),

        "quotation_data":
            report_data.get(
                "quotation_data"
            ),

        "supplier_data":
            report_data.get(
                "supplier_data"
            ),

        "purchase_history":
            report_data.get(
                "purchase_history"
            ),

        "market_cost_data":
            report_data.get(
                "market_cost_data"
            ),

        # General
        "output_path":
            OUTPUT_PATH,

        "output_file":
            output_file,

        "report_path":
            output_file,

        "data":
            report_data
    }

    # --------------------------------------------------------
    # Inspect function signature
    # --------------------------------------------------------

    try:

        signature = inspect.signature(
            report_function
        )

    except Exception:

        signature = None

    # --------------------------------------------------------
    # Call report function
    # --------------------------------------------------------

    try:

        if signature is None:

            result = report_function()

        else:

            parameters = signature.parameters

            # -----------------------------------------------
            # Function accepts **kwargs
            # -----------------------------------------------

            accepts_kwargs = any(
                parameter.kind
                == inspect.Parameter.VAR_KEYWORD
                for parameter
                in parameters.values()
            )

            if accepts_kwargs:

                result = report_function(
                    **available_data
                )

            else:

                kwargs = {}

                for name, parameter in parameters.items():

                    if (
                        parameter.kind
                        in (
                            inspect.Parameter.VAR_POSITIONAL,
                            inspect.Parameter.VAR_KEYWORD
                        )
                    ):
                        continue

                    if name in available_data:

                        kwargs[name] = (
                            available_data[name]
                        )

                # -------------------------------------------
                # If the function expects no parameters
                # -------------------------------------------

                if not kwargs:

                    result = report_function()

                else:

                    result = report_function(
                        **kwargs
                    )

        # ----------------------------------------------------
        # If report function returned HTML/string/path
        # ----------------------------------------------------

        if isinstance(result, str):

            # If it looks like HTML, save it
            if (
                "<html" in result.lower()
                or "<!doctype" in result.lower()
            ):

                with open(
                    output_file,
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(result)

            # If it returned an existing file path
            elif os.path.exists(result):

                if os.path.abspath(result) != os.path.abspath(
                    output_file
                ):

                    try:

                        with open(
                            result,
                            "r",
                            encoding="utf-8"
                        ) as source:

                            html_content = source.read()

                        with open(
                            output_file,
                            "w",
                            encoding="utf-8"
                        ) as destination:

                            destination.write(
                                html_content
                            )

                    except Exception:
                        pass

        elif isinstance(result, dict):

            possible_path = (
                result.get("output_path")
                or result.get("report_path")
                or result.get("file")
            )

            if (
                possible_path
                and os.path.exists(
                    possible_path
                )
                and os.path.abspath(
                    possible_path
                )
                != os.path.abspath(
                    output_file
                )
            ):

                with open(
                    possible_path,
                    "r",
                    encoding="utf-8"
                ) as source:

                    html_content = source.read()

                with open(
                    output_file,
                    "w",
                    encoding="utf-8"
                ) as destination:

                    destination.write(
                        html_content
                    )

        # ----------------------------------------------------
        # Verify output
        # ----------------------------------------------------

        if os.path.exists(output_file):

            print(
                "   ✓ Final HTML report generated"
            )

            print(
                f"   ✓ Report: {output_file}"
            )

            return True

        print(
            "   ✓ Report function executed"
        )

        print(
            "   ! HTML output path was not created by "
            "the report module."
        )

        return False

    except Exception as exc:

        print()
        print(
            "   ✗ Final HTML report generation failed."
        )

        print(
            f"   Error: {exc}"
        )

        return False


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print()
    print("=" * 70)
    print(" PROCUREMENT NEGOTIATION AI")
    print(" END-TO-END ANALYTICAL PIPELINE")
    print("=" * 70)

    # ========================================================
    # 1. LOAD PROCUREMENT DATA
    # ========================================================

    print()
    print("1. Loading Procurement Data...")

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

    print(
        "   ✓ All 11 procurement datasets loaded"
    )

    # ========================================================
    # CASE INFORMATION
    # ========================================================

    if negotiation_case.empty:

        raise ValueError(
            "Negotiation_Case contains no records."
        )

    current_case = (
        negotiation_case.iloc[0]
    )

    required_quantity = float(
        current_case[
            "required_quantity"
        ]
    )

    required_delivery_days = float(
        current_case[
            "required_delivery_days"
        ]
    )

    current_supplier_id = str(
        current_case[
            "current_supplier_id"
        ]
    ).strip()

    print()
    print(
        f"Current Supplier      : "
        f"{current_supplier_id}"
    )

    print(
        f"Required Quantity     : "
        f"{required_quantity:,.0f}"
    )

    print(
        f"Required Delivery     : "
        f"{required_delivery_days:,.0f} days"
    )

    # ========================================================
    # 2. DELIVERY PERFORMANCE
    # ========================================================

    print()
    print("2. Delivery Performance Analysis...")

    delivery_analysis = (
        analyze_delivery_performance(
            delivery_performance
        )
    )

    delivery_kpis = (
        calculate_supplier_delivery_kpis(
            delivery_performance
        )
    )

    save_csv(
        delivery_analysis,
        "delivery_performance_analysis.csv"
    )

    save_csv(
        delivery_kpis,
        "delivery_performance_kpis.csv"
    )

    # ========================================================
    # 3. QUOTATION SLIPPAGE
    # ========================================================

    print()
    print("3. Quotation Slippage Analysis...")

    quotation_slippage_analysis = (
        analyze_quotation_slippage(
            quotation_slippage
        )
    )

    quotation_slippage_kpis = (
        calculate_quotation_slippage_kpis(
            quotation_slippage
        )
    )

    save_csv(
        quotation_slippage_analysis,
        "quotation_slippage_analysis.csv"
    )

    save_csv(
        quotation_slippage_kpis,
        "quotation_slippage_kpis.csv"
    )

    # ========================================================
    # 4. SUPPLIER ANALYSIS
    # ========================================================

    print()
    print("4. Supplier Analysis...")

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    print()
    print("=" * 70)
    print(" SUPPLIER ANALYSIS")
    print("=" * 70)

    print(
        supplier_analysis.to_string(
            index=False
        )
    )

    save_csv(
        supplier_analysis,
        "supplier_analysis.csv"
    )

    # ========================================================
    # 5. OUTSIDE OPTION ANALYSIS
    # ========================================================

    print()
    print("5. Outside Option Analysis...")

    outside_options = (
        calculate_outside_options(
            supplier_analysis,
            market_cost_data,
            required_quantity
        )
    )

    if outside_options.empty:

        raise ValueError(
            "No outside-option suppliers were produced. "
            "BATNA cannot be calculated."
        )

    save_csv(
        outside_options,
        "outside_option_analysis.csv"
    )

    # ========================================================
    # 6. BATNA ANALYSIS
    # ========================================================

    print()
    print("6. BATNA Analysis...")

    # --------------------------------------------------------
    # Make sure cost is numeric
    # --------------------------------------------------------

    if (
        "effective_outside_option_cost"
        not in outside_options.columns
    ):

        raise ValueError(
            "Outside-option result does not contain "
            "'effective_outside_option_cost'."
        )

    outside_options[
        "effective_outside_option_cost"
    ] = pd.to_numeric(
        outside_options[
            "effective_outside_option_cost"
        ],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Remove invalid costs
    # --------------------------------------------------------

    outside_options = (
        outside_options
        .dropna(
            subset=[
                "effective_outside_option_cost"
            ]
        )
        .copy()
    )

    # --------------------------------------------------------
    # Remove current supplier
    # --------------------------------------------------------

    batna_candidates = (
        outside_options.copy()
    )

    if "supplier_id" in batna_candidates.columns:

        batna_candidates = (
            batna_candidates[
                batna_candidates[
                    "supplier_id"
                ]
                .astype(str)
                .str.strip()
                != current_supplier_id
            ]
            .copy()
        )

    if batna_candidates.empty:

        raise ValueError(
            "No alternative supplier remains "
            "after excluding the current supplier."
        )

    # --------------------------------------------------------
    # Select lowest valid alternative cost
    # --------------------------------------------------------

    batna_index = (
        batna_candidates[
            "effective_outside_option_cost"
        ].idxmin()
    )

    batna_row = (
        batna_candidates.loc[
            batna_index
        ]
    )

    batna_supplier_id = str(
        batna_row[
            "supplier_id"
        ]
    )

    batna_supplier_name = str(
        batna_row[
            "supplier_name"
        ]
    )

    batna_cost = float(
        batna_row[
            "effective_outside_option_cost"
        ]
    )

    batna = {

        "batna_supplier_id":
            batna_supplier_id,

        "batna_supplier_name":
            batna_supplier_name,

        "batna_cost":
            batna_cost
    }

    batna_result = pd.DataFrame([
        batna
    ])

    save_csv(
        batna_result,
        "batna_result.csv"
    )

    print()
    print(
        f"   BATNA Supplier : "
        f"{batna_supplier_name}"
    )

    print(
        f"   BATNA Cost     : "
        f"₹{batna_cost:,.2f}"
    )

    print(
        f"   BATNA / Unit   : "
        f"₹{batna_cost / required_quantity:,.2f}"
    )

    # ========================================================
    # 7. RESERVATION VALUE
    # ========================================================

    print()
    print("7. Reservation Value...")

    reservation_value = (
        calculate_reservation_value(
            batna
        )
    )

    reservation_per_unit = (
        reservation_value
        / required_quantity
        if required_quantity != 0
        else 0
    )

    reservation_result = pd.DataFrame([
        {

            "batna_supplier_id":
                batna_supplier_id,

            "batna_supplier_name":
                batna_supplier_name,

            "reservation_value":
                reservation_value,

            "reservation_value_per_unit":
                reservation_per_unit
        }
    ])

    save_csv(
        reservation_result,
        "reservation_value.csv"
    )

    print(
        f"   Reservation Value : "
        f"₹{reservation_value:,.2f}"
    )

    print(
        f"   Reservation / Unit : "
        f"₹{reservation_per_unit:,.2f}"
    )

    # ========================================================
    # 8. ZOPA
    # ========================================================

    print()
    print("8. ZOPA Analysis...")

    zopa_result = calculate_zopa(
        reservation_value,
        supplier_analysis,
        quotation_data,
        negotiation_case
    )

    save_csv(
        zopa_result,
        "zopa_analysis.csv"
    )

    # ========================================================
    # 9. NASH BARGAINING
    # ========================================================

    print()
    print("9. Nash Bargaining...")

    nash_result = calculate_nash_bargaining(
        supplier_analysis,
        purchase_history,
        negotiation_case,
        reservation_value
    )

    save_csv(
        nash_result,
        "nash_bargaining.csv"
    )

    # ========================================================
    # 10. SUPPLIER SIGNALLING
    # ========================================================

    print()
    print("10. Supplier Signalling...")

    signalling_result = analyze_signals(
        supplier_signals
    )

    save_csv(
        signalling_result,
        "signalling_analysis.csv"
    )

    # ========================================================
    # 11. CREDIBILITY
    # ========================================================

    print()
    print("11. Credibility Analysis...")

    credibility_result = (
        assess_credibility(
            signalling_result
        )
    )

    save_csv(
        credibility_result,
        "credibility_analysis.csv"
    )

    # ========================================================
    # 12. OUTSIDE-OPTION VERIFICATION
    # ========================================================

    print()
    print(
        "12. Outside-Option Verification..."
    )

    verification_result = (
        verify_outside_option_signals(
            credibility_result
        )
    )

    save_csv(
        verification_result,
        "outside_option_verification.csv"
    )

    # ========================================================
    # 13. INFORMATION ASYMMETRY
    # ========================================================

    print()
    print("13. Information Asymmetry...")

    information_result = (
        analyze_information_asymmetry(
            credibility_result
        )
    )

    save_csv(
        information_result,
        "information_asymmetry.csv"
    )

    # ========================================================
    # 14. TIMING / HOLD-UP
    # ========================================================

    print()
    print("14. Timing Analysis...")

    timing_result = analyze_timing(
        supplier_analysis,
        negotiation_case
    )

    save_csv(
        timing_result,
        "timing_analysis.csv"
    )

    # ========================================================
    # 15. SUPPLIER RISK
    # ========================================================

    print()
    print("15. Supplier Risk Analysis...")

    supplier_risk_result = (
        calculate_supplier_risk(
            supplier_analysis,
            delivery_kpis,
            quotation_slippage_kpis,
            timing_result,
            information_result
        )
    )

    save_csv(
        supplier_risk_result,
        "supplier_risk_analysis.csv"
    )

    # ========================================================
    # 16. SUPPLIER TIMELINE
    # ========================================================

    print()
    print("16. Supplier Timeline Analysis...")

    supplier_timeline_result = (
        calculate_supplier_timeline(
            supplier_timeline
        )
    )

    save_csv(
        supplier_timeline_result,
        "supplier_timeline_analysis.csv"
    )

    # ========================================================
    # 17. SHOULD-COST
    # ========================================================

    print()
    print("17. Should-Cost Analysis...")

    should_cost_result = (
        calculate_should_cost(
            market_cost_data,
            quotation_data
        )
    )

    save_csv(
        should_cost_result,
        "should_cost_analysis.csv"
    )

    # ========================================================
    # 18. TOTAL COST OF OWNERSHIP
    # ========================================================

    print()
    print(
        "18. Total Cost of Ownership Analysis..."
    )

    (
        tco_detail,
        tco_summary
    ) = calculate_complete_tco(

        quotation_data=quotation_data,

        market_cost_data=market_cost_data,

        supplier_data=supplier_data,

        delivery_performance=delivery_kpis,

        annual_financing_rate=0.0
    )

    save_csv(
        tco_detail,
        "tco_analysis.csv"
    )

    save_csv(
        tco_summary,
        "tco_supplier_summary.csv"
    )

    # ========================================================
    # 19. VALUE-AT-STAKE
    # ========================================================

    print()
    print("19. Value-at-Stake Analysis...")

    (
        value_at_stake_detail,
        value_at_stake_summary
    ) = calculate_complete_value_at_stake(

        quotation_data=quotation_data,

        tco_summary=tco_summary,

        negotiation_case=negotiation_case,

        batna_result=batna_result
    )

    save_csv(
        value_at_stake_detail,
        "value_at_stake_analysis.csv"
    )

    save_csv(
        value_at_stake_summary,
        "value_at_stake_supplier_summary.csv"
    )

    # ========================================================
    # 20. SHAPLEY VALUE ANALYSIS
    # ========================================================

    print()
    print("20. Shapley Value Analysis...")

    # --------------------------------------------------------
    # Synthetic / illustrative negotiation lever values.
    #
    # These are NOT real Knorr-Bremse values.
    # --------------------------------------------------------

    lever_values = {

        "price_concession":
            50000,

        "quantity_commitment":
            20000,

        "payment_terms":
            10000,

        "delivery_improvement":
            15000
    }

    shapley_values = (
        calculate_shapley_values(
            lever_values
        )
    )

    total_negotiation_value = sum(
        lever_values.values()
    )

    shapley_rows = []

    for lever, value in (
        lever_values.items()
    ):

        shapley_value = (
            shapley_values[lever]
        )

        contribution_percentage = (

            shapley_value
            /
            total_negotiation_value
            *
            100

            if total_negotiation_value != 0
            else 0
        )

        shapley_rows.append({

            "negotiation_lever":
                lever,

            "lever_value":
                value,

            "shapley_value":
                shapley_value,

            "contribution_percentage":
                contribution_percentage
        })

    shapley_result = pd.DataFrame(
        shapley_rows
    )

    shapley_result = (
        shapley_result
        .sort_values(
            by="shapley_value",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    shapley_total = pd.DataFrame([
        {
            "total_negotiation_value":
                total_negotiation_value
        }
    ])

    save_csv(
        shapley_result,
        "shapley_analysis.csv"
    )

    save_csv(
        shapley_total,
        "shapley_total_value.csv"
    )

    print()
    print(
        shapley_result.to_string(
            index=False
        )
    )

    # ========================================================
    # 21. FINAL NEGOTIATION DECISION
    # ========================================================

    print()
    print(
        "21. Final Negotiation Decision..."
    )

    final_decision_result = (
        build_negotiation_decision(

            nash_result=nash_result,

            zopa_result=zopa_result,

            timing_result=timing_result,

            supplier_risk_result=
                supplier_risk_result,

            should_cost_result=
                should_cost_result,

            tco_result=
                tco_summary,

            value_at_stake_result=
                value_at_stake_summary,

            credibility_result=
                credibility_result,

            verification_result=
                verification_result,

            information_result=
                information_result,

            shapley_result=
                shapley_result
        )
    )

    # --------------------------------------------------------
    # Required quantity is passed forward to strategy.
    # --------------------------------------------------------

    final_decision_result[
        "required_quantity"
    ] = required_quantity

    save_csv(
        final_decision_result,
        "final_negotiation_decision.csv"
    )

    # ========================================================
    # FINAL DECISION DISPLAY
    # ========================================================

    print()
    print("=" * 70)
    print(" FINAL NEGOTIATION DECISION")
    print("=" * 70)

    if (
        isinstance(
            final_decision_result,
            pd.DataFrame
        )
        and not final_decision_result.empty
    ):

        display_columns = [
            "supplier_id",
            "supplier_name"
        ]

        optional_columns = [

            "recommended_target_price",

            "walk_away_price",

            "buyer_reservation_value",

            "nash_price_per_unit",

            "nash_total_price",

            "zopa_exists",

            "negotiation_priority",

            "recommendation",

            "recommended_buyer_action",

            "negotiation_decision_score",

            "decision_rank"
        ]

        for column in optional_columns:

            if (
                column
                in final_decision_result.columns
            ):

                display_columns.append(
                    column
                )

        available_columns = [

            column

            for column
            in display_columns

            if (
                column
                in final_decision_result.columns
            )
        ]

        if available_columns:

            print()

            print(
                final_decision_result[
                    available_columns
                ].to_string(
                    index=False
                )
            )

    # ========================================================
    # 22. NEGOTIATION STRATEGY
    # ========================================================

    print()
    print("22. Negotiation Strategy...")

    negotiation_strategy_result = (
        build_negotiation_strategy(

            final_analysis=
                final_decision_result,

            zopa_analysis=
                zopa_result,

            shapley_analysis=
                shapley_result
        )
    )

    save_csv(
        negotiation_strategy_result,
        "negotiation_strategy.csv"
    )

    # --------------------------------------------------------
    # Stage 22 display
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(" NEGOTIATION STRATEGY ")
    print("=" * 70)

    strategy_display_columns = [

        "supplier_id",

        "supplier_name",

        "zopa_exists",

        "zopa_low_per_unit",

        "zopa_high_per_unit",

        "current_offer_per_unit",

        "opening_price_per_unit",

        "target_price_per_unit",

        "walk_away_price_per_unit",

        "primary_negotiation_levers",

        "negotiation_posture",

        "supplier_specific_strategy"
    ]

    strategy_available_columns = [

        column

        for column
        in strategy_display_columns

        if (
            column
            in negotiation_strategy_result.columns
        )
    ]

    if strategy_available_columns:

        print()

        print(
            negotiation_strategy_result[
                strategy_available_columns
            ].to_string(
                index=False
            )
        )

    # ========================================================
    # 23. NEGOTIATION BRIEF
    # ========================================================

    print()
    print("23. Negotiation Brief...")

    (
        negotiation_brief_summary,
        negotiation_brief_result
    ) = build_negotiation_brief(

        negotiation_case=
            negotiation_case,

        final_decision_result=
            final_decision_result,

        strategy_result=
            negotiation_strategy_result,

        shapley_result=
            shapley_result
    )

    save_csv(
        negotiation_brief_summary,
        "negotiation_brief_summary.csv"
    )

    save_csv(
        negotiation_brief_result,
        "negotiation_brief.csv"
    )

    # --------------------------------------------------------
    # Stage 23 display
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(" NEGOTIATION BRIEF ")
    print("=" * 70)

    brief_display_columns = [

        "supplier_id",

        "supplier_name",

        "current_offer_per_unit",

        "opening_price_per_unit",

        "target_price_per_unit",

        "walk_away_price_per_unit",

        "negotiation_posture",

        "supplier_specific_strategy"
    ]

    brief_available_columns = [

        column

        for column
        in brief_display_columns

        if (
            column
            in negotiation_brief_result.columns
        )
    ]

    if brief_available_columns:

        print()

        print(
            negotiation_brief_result[
                brief_available_columns
            ].to_string(
                index=False
            )
        )

    # ========================================================
    # TOP NEGOTIATION RECOMMENDATION
    # ========================================================

    if (
        isinstance(
            final_decision_result,
            pd.DataFrame
        )
        and not final_decision_result.empty
    ):

        # Make sure ranking is respected.
        # Do not assume the original row order.
        top_candidates = (
            final_decision_result.copy()
        )

        if (
            "decision_rank"
            in top_candidates.columns
        ):

            top_candidates[
                "decision_rank"
            ] = pd.to_numeric(
                top_candidates[
                    "decision_rank"
                ],
                errors="coerce"
            )

            top_candidates = (
                top_candidates
                .sort_values(
                    by="decision_rank",
                    ascending=True
                )
            )

        top_row = (
            top_candidates.iloc[0]
        )

        print()
        print("=" * 70)
        print(" TOP NEGOTIATION RECOMMENDATION")
        print("=" * 70)

        if "supplier_name" in top_row.index:

            print(
                f"Supplier       : "
                f"{top_row['supplier_name']}"
            )

        if "supplier_id" in top_row.index:

            print(
                f"Supplier ID    : "
                f"{top_row['supplier_id']}"
            )

        if (
            "recommended_target_price"
            in top_row.index
        ):

            if pd.notna(
                top_row[
                    "recommended_target_price"
                ]
            ):

                print(
                    f"Target Price   : "
                    f"₹{float(top_row['recommended_target_price']):,.2f}"
                )

        if (
            "walk_away_price"
            in top_row.index
        ):

            if pd.notna(
                top_row[
                    "walk_away_price"
                ]
            ):

                print(
                    f"Walk-Away Price: "
                    f"₹{float(top_row['walk_away_price']):,.2f}"
                )

        if (
            "negotiation_priority"
            in top_row.index
        ):

            print(
                f"Priority       : "
                f"{top_row['negotiation_priority']}"
            )

        if (
            "recommendation"
            in top_row.index
        ):

            print(
                f"Recommendation : "
                f"{top_row['recommendation']}"
            )

        if (
            "recommended_buyer_action"
            in top_row.index
        ):

            print(
                f"Buyer Action   : "
                f"{top_row['recommended_buyer_action']}"
            )

    # ========================================================
    # 24. FINAL NEGOTIATION REPORT
    # ========================================================

    print()
    print("24. Final Negotiation Report...")

    report_data = {

        # Raw data
        "supplier_data":
            supplier_data,

        "purchase_history":
            purchase_history,

        "quotation_data":
            quotation_data,

        "negotiation_history":
            negotiation_history,

        "market_cost_data":
            market_cost_data,

        "negotiation_case":
            negotiation_case,

        "supplier_signals":
            supplier_signals,

        "supplier_location":
            supplier_location,

        "delivery_performance":
            delivery_performance,

        "quotation_slippage":
            quotation_slippage,

        "supplier_timeline":
            supplier_timeline,

        # Core analysis
        "supplier_analysis":
            supplier_analysis,

        "outside_options":
            outside_options,

        "batna":
            batna,

        "batna_result":
            batna_result,

        "reservation_value":
            reservation_value,

        "reservation_per_unit":
            reservation_per_unit,

        "reservation_result":
            reservation_result,

        "zopa_result":
            zopa_result,

        "nash_result":
            nash_result,

        # Game theory
        "signalling_result":
            signalling_result,

        "credibility_result":
            credibility_result,

        "verification_result":
            verification_result,

        "information_result":
            information_result,

        "timing_result":
            timing_result,

        # Risk / cost
        "delivery_kpis":
            delivery_kpis,

        "quotation_slippage_kpis":
            quotation_slippage_kpis,

        "supplier_risk_result":
            supplier_risk_result,

        "supplier_timeline_result":
            supplier_timeline_result,

        "should_cost_result":
            should_cost_result,

        "tco_detail":
            tco_detail,

        "tco_summary":
            tco_summary,

        "value_at_stake_detail":
            value_at_stake_detail,

        "value_at_stake_summary":
            value_at_stake_summary,

        # Shapley
        "shapley_result":
            shapley_result,

        "shapley_total":
            shapley_total,

        # Final decision
        "final_decision_result":
            final_decision_result,

        "negotiation_strategy_result":
            negotiation_strategy_result,

        "negotiation_brief_summary":
            negotiation_brief_summary,

        "negotiation_brief_result":
            negotiation_brief_result
    }

    report_success = (
        generate_final_html_report(
            report_data
        )
    )

    # ========================================================
    # FINAL PIPELINE SUMMARY
    # ========================================================

    print()
    print("=" * 70)

    if report_success:

        print(
            " PROCUREMENT NEGOTIATION AI "
            "PIPELINE COMPLETED SUCCESSFULLY"
        )

    else:

        print(
            " PROCUREMENT NEGOTIATION AI "
            "ANALYTICAL PIPELINE COMPLETED"
        )

        print(
            " WARNING: Final HTML report was not generated."
        )

    print("=" * 70)

    print()
    print("Key outputs generated:")

    output_list = [

        "Delivery Performance",

        "Quotation Slippage",

        "Supplier Analysis",

        "Outside Option",

        "BATNA",

        "Reservation Value",

        "ZOPA",

        "Nash Bargaining",

        "Supplier Signalling",

        "Credibility",

        "Outside-Option Verification",

        "Information Asymmetry",

        "Timing / Hold-Up",

        "Supplier Risk",

        "Supplier Timeline",

        "Should-Cost",

        "Total Cost of Ownership",

        "Value-at-Stake",

        "Shapley Value",

        "Final Negotiation Decision",

        "Negotiation Strategy",

        "Negotiation Brief",

        "Final Negotiation Report"
    ]

    for item in output_list:

        print(
            f"   ✓ {item}"
        )

    print()
    print(
        f"CSV outputs : {OUTPUT_PATH}"
    )

    report_path = os.path.join(
        OUTPUT_PATH,
        "final_negotiation_report.html"
    )

    if os.path.exists(report_path):

        print(
            f"HTML report : {report_path}"
        )

    print()


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()