"""Canonical concept map for the SixGates v1 data model.

Each canonical concept lists ``candidates`` (synonym tags for the same line
item; when several are present for a year the latest filed wins and any
disagreement beyond rounding is flagged as ``ambiguous``), then ``fallbacks``
(broader or narrower tags used only when no synonym exists, always noted), then
``components`` (each a priority list; the canonical value is their sum, reported
as ``partial_sum`` when a component is absent). ``absent_ok`` marks balance sheet
lines that legitimately may not exist (an absent component is flagged at low
severity, never silently taken as zero). Nothing is ever estimated.

The us-gaap candidates were chosen after surveying the companyfacts of Apple,
Coca-Cola and Moody's (October 2026); the ifrs-full candidates after inspecting
the ESEF xBRL-JSON of LVMH and OMV Petrom.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConceptSpec:
    """Mapping rule for one canonical concept.

    ``kind`` is ``duration`` (income statement, cash flow) or ``instant``
    (balance sheet). ``candidates`` are tried in order; ``components`` are
    summed when no candidate exists. ``sign`` flips tags reported as positive
    outflows into the canonical sign convention (outflows positive here, so 1).
    """

    name: str
    kind: str
    candidates: tuple[str, ...]
    fallbacks: tuple[str, ...] = field(default_factory=tuple)
    components: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    unit: str = "USD"
    absent_ok: bool = False
    note: str = ""


US_GAAP: tuple[ConceptSpec, ...] = (
    ConceptSpec("revenue", "duration", (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
    ), note="ASC 606 tag from FY2018 (Apple switched in its FY2019 10-K); Coca-Cola kept Revenues"),
    ConceptSpec("operating_income", "duration", ("OperatingIncomeLoss",)),
    ConceptSpec("pretax_income", "duration", (
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    ), note="Moody's switched between the two tags in FY2019"),
    ConceptSpec("income_tax", "duration", ("IncomeTaxExpenseBenefit",)),
    ConceptSpec("net_income", "duration", ("NetIncomeLoss",),
                fallbacks=("ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"),
                note="NetIncomeLoss is attributable to the parent; ProfitLoss includes minorities (fallback only)"),
    ConceptSpec("d_and_a", "duration", (
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
        "DepreciationAmortizationAndAccretionNet",
    ), components=(("Depreciation",), ("AmortizationOfIntangibleAssets",)),
        note="Moody's uses DepreciationAndAmortization; Apple used three tags over time and reused one for a note value"),
    ConceptSpec("capex", "duration", (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
        "PaymentsForCapitalImprovements",
    ), note="cash outflow, positive; Apple pre-FY2013 used PaymentsToAcquireProductiveAssets"),
    ConceptSpec("cfo", "duration", ("NetCashProvidedByUsedInOperatingActivities",),
                fallbacks=("NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",)),
    ConceptSpec("cash", "instant", ("CashAndCashEquivalentsAtCarryingValue",),
                fallbacks=("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",),
                note="strict cash; the restricted-cash total is a fallback only"),
    ConceptSpec("st_investments", "instant", (), components=(
        ("ShortTermInvestments", "OtherShortTermInvestments"),
        ("MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesCurrent", "MarketableSecurities"),
    ), absent_ok=True, note="Coca-Cola reports short-term investments and marketable securities as two lines; summed"),
    ConceptSpec("st_borrowings", "instant", (
        "NotesAndLoansPayable",
        "NotesAndLoansPayableCurrent",
        "ShortTermBorrowings",
        "DebtCurrent",
    ), fallbacks=("CommercialPaper",), absent_ok=True,
        note="Coca-Cola used four tags in ten years, one of them a custom extension (FY2015 to FY2016); "
             "CommercialPaper is a component used as fallback"),
    ConceptSpec("ltd_current", "instant", (
        "LongTermDebtCurrent",
        "LongTermDebtAndCapitalLeaseObligationsCurrent",
    ), absent_ok=True, note="lease-inclusive tag from FY2024 at Coca-Cola"),
    ConceptSpec("debt_long", "instant", (
        "LongTermDebtNoncurrent",
        "LongTermDebtAndCapitalLeaseObligations",
    ), fallbacks=("LongTermDebt",),
        note="lease-inclusive tag from FY2024 at Coca-Cola; LongTermDebt (total incl. current) only as fallback, "
             "needed by Moody's FY2020 when no current portion existed"),
    ConceptSpec("interest_expense", "duration", (
        "InterestExpense",
        "InterestExpenseBorrowings",
        "InterestExpenseNonoperating",
    ), fallbacks=("InterestExpenseDebt",),
        note="Moody's uses InterestExpenseBorrowings; Apple stopped tagging it after FY2023"),
    ConceptSpec("equity", "instant", ("StockholdersEquity",),
                fallbacks=("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",),
                note="parent equity first; Moody's equity was negative FY2015 to FY2017"),
    ConceptSpec("goodwill", "instant", ("Goodwill",),
                note="Apple stopped tagging goodwill after FY2017 (folded into other non-current assets)"),
    ConceptSpec("intangibles", "instant", ("IntangibleAssetsNetExcludingGoodwill",), components=(
        ("IndefiniteLivedTrademarks",),
        ("IndefiniteLivedFranchiseRights",),
        ("OtherIntangibleAssetsNet", "FiniteLivedIntangibleAssetsNet"),
    ), absent_ok=True, note="Coca-Cola: trademarks plus other intangibles; FY2024 onwards only trademarks carry a standard tag"),
    ConceptSpec("current_assets", "instant", ("AssetsCurrent",)),
    ConceptSpec("current_liabilities", "instant", ("LiabilitiesCurrent",)),
    ConceptSpec("ppe_net", "instant", (
        "PropertyPlantAndEquipmentNet",
        "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
    )),
    ConceptSpec("diluted_shares", "duration", ("WeightedAverageNumberOfDilutedSharesOutstanding",), unit="shares"),
    ConceptSpec("dividends_paid", "duration", (
        "PaymentsOfDividendsCommonStock",
        "PaymentsOfDividends",
        "PaymentsOfDividendsAndDividendEquivalentsOnCommonStockAndRestrictedStockUnits",
    ), note="Moody's switched to PaymentsOfDividendsCommonStock in FY2017; Apple restated FY2016 to include dividend equivalents"),
    ConceptSpec("share_repurchases", "duration", ("PaymentsForRepurchaseOfCommonStock",)),
)


IFRS: tuple[ConceptSpec, ...] = (
    ConceptSpec("revenue", "duration", ("ifrs-full:Revenue", "ifrs-full:RevenueFromContractsWithCustomers"), unit="EUR"),
    ConceptSpec("operating_income", "duration", ("ifrs-full:ProfitLossFromOperatingActivities",), unit="EUR",
                note="not a mandatory IFRS subtotal; issuers often use an extension (LVMH: profit from recurring operations)"),
    ConceptSpec("pretax_income", "duration", ("ifrs-full:ProfitLossBeforeTax",), unit="EUR"),
    ConceptSpec("income_tax", "duration", ("ifrs-full:IncomeTaxExpenseContinuingOperations",), unit="EUR"),
    ConceptSpec("net_income", "duration", ("ifrs-full:ProfitLossAttributableToOwnersOfParent",),
                fallbacks=("ifrs-full:ProfitLoss",), unit="EUR"),
    ConceptSpec("d_and_a", "duration", (
        "ifrs-full:DepreciationAndAmortisationExpense",
        "ifrs-full:AdjustmentsForDepreciationAndAmortisationExpense",
    ), fallbacks=(
        "ifrs-full:DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss",
        "ifrs-full:AdjustmentsForDepreciationAndAmortisationExpenseAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss",
    ), components=(
        ("ifrs-full:DepreciationPropertyPlantAndEquipment", "ifrs-full:AdjustmentsForDepreciationExpense"),
        ("ifrs-full:AmortisationIntangibleAssetsOtherThanGoodwill", "ifrs-full:AdjustmentsForAmortisationExpense"),
        ("ifrs-full:DepreciationRightofuseAssets",),
    ), unit="EUR", note="cash-flow adjustment tag usually; IFRS 16 right-of-use depreciation is included when tagged"),
    ConceptSpec("capex", "duration", (
        "ifrs-full:PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets",
    ), components=(
        ("ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",),
        ("ifrs-full:PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities",),
    ), unit="EUR"),
    ConceptSpec("cfo", "duration", ("ifrs-full:CashFlowsFromUsedInOperatingActivities",),
                fallbacks=("ifrs-full:CashFlowsFromUsedInOperations",), unit="EUR",
                note="OMV Petrom tags its net operating cash flow with the broader CashFlowsFromUsedInOperations"),
    ConceptSpec("cash", "instant", ("ifrs-full:CashAndCashEquivalents",), unit="EUR"),
    ConceptSpec("st_investments", "instant", ("ifrs-full:CurrentFinancialAssetsAtFairValueThroughProfitOrLoss", "ifrs-full:OtherCurrentFinancialAssets"),
                unit="EUR", absent_ok=True, note="no clean IFRS equivalent; issuers use extensions"),
    ConceptSpec("st_borrowings", "instant", ("ifrs-full:ShorttermBorrowings", "ifrs-full:CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings"),
                unit="EUR", absent_ok=True),
    ConceptSpec("ltd_current", "instant", ("ifrs-full:CurrentPortionOfLongtermBorrowings",), unit="EUR", absent_ok=True,
                note="often inside ShorttermBorrowings already; do not double count"),
    ConceptSpec("debt_long", "instant", ("ifrs-full:LongtermBorrowings", "ifrs-full:NoncurrentPortionOfNoncurrentBorrowings"), unit="EUR"),
    ConceptSpec("interest_expense", "duration", ("ifrs-full:InterestExpense",), fallbacks=("ifrs-full:FinanceCosts",), unit="EUR"),
    ConceptSpec("equity", "instant", ("ifrs-full:EquityAttributableToOwnersOfParent",), fallbacks=("ifrs-full:Equity",), unit="EUR"),
    ConceptSpec("goodwill", "instant", ("ifrs-full:Goodwill",), unit="EUR"),
    ConceptSpec("intangibles", "instant", ("ifrs-full:IntangibleAssetsOtherThanGoodwill",), unit="EUR"),
    ConceptSpec("current_assets", "instant", ("ifrs-full:CurrentAssets",),
                fallbacks=("ifrs-full:CurrentAssetsOtherThanAssetsOrDisposalGroupsClassifiedAsHeldForSaleOrAsHeldForDistributionToOwners",), unit="EUR"),
    ConceptSpec("current_liabilities", "instant", ("ifrs-full:CurrentLiabilities",),
                fallbacks=("ifrs-full:CurrentLiabilitiesOtherThanLiabilitiesIncludedInDisposalGroupsClassifiedAsHeldForSale",), unit="EUR"),
    ConceptSpec("ppe_net", "instant", ("ifrs-full:PropertyPlantAndEquipment",), unit="EUR"),
    ConceptSpec("diluted_shares", "duration", ("ifrs-full:AdjustedWeightedAverageShares",), fallbacks=("ifrs-full:WeightedAverageShares",),
                unit="shares", note="rarely tagged under ESEF (only primary statements are mandatory)"),
    ConceptSpec("dividends_paid", "duration", (
        "ifrs-full:DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities",
        "ifrs-full:DividendsPaidClassifiedAsFinancingActivities",
    ), unit="EUR"),
    ConceptSpec("share_repurchases", "duration", ("ifrs-full:PaymentsToAcquireOrRedeemEntitysShares",), unit="EUR"),
)

# Concepts that a fiscal year must have for the ten-year rule (gate 3 inputs).
REQUIRED_FOR_TEN_YEAR_RULE: tuple[str, ...] = (
    "revenue", "operating_income", "pretax_income", "income_tax", "net_income",
    "d_and_a", "capex", "cfo", "cash", "current_assets", "current_liabilities", "ppe_net",
)


def spec_by_name(specs: tuple[ConceptSpec, ...]) -> dict[str, ConceptSpec]:
    """Index a spec tuple by canonical name."""
    return {s.name: s for s in specs}
