from pathlib import Path

import numpy as np
import pandas as pd

LATE_PAYMENT_CODES = [96, 98]
DEBT_RATIO_CAP = 5


def build_silver(input_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(input_path)
    # D1/2
    df = rename_columns(df)
    # D6
    df = drop_age_below_18(df)
    # D3
    df = income_missing_column(df)
    # D4
    df = fill_missing_dependents(df)
    # D5
    df = late_payment_flag(df)
    # D7
    df = utilization_above_2(df)
    # D8
    df = set_debt_ratio_missing(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return df


# Decision 1/2: Rename columns to fit a more commonly found theme.
def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename({"Unnamed: 0": "id",
           "SeriousDlqin2yrs": "serious_dlq_2yrs", 
           "RevolvingUtilizationOfUnsecuredLines": "revolving_util", 
           "NumberOfTime30-59DaysPastDueNotWorse": "late_30_59",
           "DebtRatio": "debt_ratio", 
           "MonthlyIncome": "monthly_income", 
           "NumberOfOpenCreditLinesAndLoans": "open_credit_lines",
           "NumberOfTimes90DaysLate": "late_90_plus", 
           "NumberRealEstateLoansOrLines": "real_estate_loans", 
           "NumberOfTime60-89DaysPastDueNotWorse": "late_60_89",
           "NumberOfDependents": "dependents"}, 
          axis = "columns")
    return renamed


# Decision 3: Add incoming missing flag column.
def income_missing_column(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()
    copy["income_missing"] = np.where((copy["monthly_income"].isnull()), 1, 0)
    return copy


# Decision 4: Fill missing dependents with 0.
def fill_missing_dependents(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()
    copy["dependents"] = copy["dependents"].fillna(0).astype(int)
    return copy


# Decision 5: Late payment flag.
def late_payment_flag(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()
    mask = (copy["late_30_59"].isin(LATE_PAYMENT_CODES)) | (copy["late_60_89"].isin(LATE_PAYMENT_CODES)) | (copy["late_90_plus"].isin(LATE_PAYMENT_CODES))
    copy["late_code_96_98"] = np.where(mask, 1, 0)
    copy.loc[mask, ["late_30_59", "late_60_89", "late_90_plus"]] = 0
    return copy


# Decision 6: Remove rows where age is below 18. 
# There is one row which is 0, however for future proofing I am making the cut off 18.
def drop_age_below_18(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["age"] >= 18].reset_index(drop=True)


# Decision 7: Utilization above 2 becomes missing.
def utilization_above_2(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()
    copy.loc[(copy["revolving_util"] > 2), ["revolving_util"]] = np.nan
    return copy


# Decision 8: Set debt ratio missing where income is missing
def set_debt_ratio_missing(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()
    copy.loc[(copy["income_missing"] == 1), ["debt_ratio"]] = np.nan
    copy["debt_ratio"] = copy["debt_ratio"].clip(upper=DEBT_RATIO_CAP)
    return copy