import pandas as pd

PATH = "data/raw/cs-training.csv"

df = pd.read_csv(PATH)
# print(df.shape)
# print(df.info())
# print(df.duplicated())
# print(df.value_counts())

# Unnamed column
print(df.columns[0])

# Target mean = 0.06684
print(df['SeriousDlqin2yrs'].mean())

# Empty values 
print(df.isna().sum())
print((df["NumberOfDependents"].isna() & df["MonthlyIncome"].isna()).sum())

# Aged 0
under_18 = (df[df['age'] < 18])
print(under_18['age'])

# Very late payments
print(df["NumberOfTimes90DaysLate"].value_counts().sort_index())

# Credit card usage 
print(df["RevolvingUtilizationOfUnsecuredLines"].describe())
print(df["RevolvingUtilizationOfUnsecuredLines"].value_counts().sort_index())

# High debt ratio for null monthly income
print(df.groupby(df["MonthlyIncome"].isna())["DebtRatio"].median())

# Duplicate rows
print(df.iloc[:, 1:].duplicated().sum())