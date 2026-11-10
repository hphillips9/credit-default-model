import pandas as pd
from credit_pipeline.bronze import build_bronze


def test_build_bronze(tmp_path):
    csv_file = tmp_path / "sample.csv"
    output = tmp_path / "out.parquet"
    csv_file.write_text(
        """,SeriousDlqin2yrs,RevolvingUtilizationOfUnsecuredLines,age,NumberOfTime30-59DaysPastDueNotWorse,DebtRatio,MonthlyIncome,NumberOfOpenCreditLinesAndLoans,NumberOfTimes90DaysLate,NumberRealEstateLoansOrLines,NumberOfTime60-89DaysPastDueNotWorse,NumberOfDependents
1,1,0.7,45,2,0.8,9000,13,0,6,0,2
2,0,0.9,40,0,0.2,3000,4,0,0,0,1
3,0,0.6,35,1,0.1,,2,1,0,0,0""")

    df = build_bronze(csv_file, output)

    assert output.exists()
    out_file = pd.read_parquet(output)
    assert out_file.shape[0] == 3
    assert out_file.shape[1] == 14
    assert "_loaded_at" in out_file.columns
    assert "_source_file" in out_file.columns
    assert out_file.iloc[2]["age"] == 35
    assert out_file["MonthlyIncome"].isnull()[2]
    assert len(out_file["_loaded_at"].value_counts()) == 1
    assert len(out_file[out_file["_source_file"] != csv_file.name]) == 0
    assert(df.shape == out_file.shape)