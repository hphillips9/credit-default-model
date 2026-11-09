# Decisions

Each decision has four parts: what I found, the options, what I decided, and why.
Code comments point back here by number (e.g. "see D5").

## D1: The unnamed first column

**What I found:** The first column has a blank header (pandas reads it as "Unnamed: 0"). It holds the whole numbers 1 to 150,000, each appearing exactly once. It's a row counter from the original file, not information about the person.

**Options:**
1. Drop it.
2. Rename it to `id` and keep it.

**Decision:** Option 2. Rename it to `id`, keep it in every layer, and never use it as a model feature.

**Why:** Need to use the id for uniqueness.


## D2: Column names

**What I found:** The original names are long CamelCase with hyphens and spaces in meaning (e.g. `NumberOfTime30-59DaysPastDueNotWorse`). They're awkward to type, the hyphens clash with SQL, and some names are misleading (`DebtRatio` isn't always a ratio; see D8).

**Options:**
1. Keep the original names.
2. Rename everything to short, clear snake_case.

**Decision:** Option 2, using this mapping:

| Original | New name |
|---|---|
| (unnamed) | `id` |
| SeriousDlqin2yrs | `serious_dlq_2yrs` (the target) |
| RevolvingUtilizationOfUnsecuredLines | `revolving_util` |
| age | `age` |
| NumberOfTime30-59DaysPastDueNotWorse | `late_30_59` |
| NumberOfTime60-89DaysPastDueNotWorse | `late_60_89` |
| NumberOfTimes90DaysLate | `late_90_plus` |
| DebtRatio | `debt_ratio` |
| MonthlyIncome | `monthly_income` |
| NumberOfOpenCreditLinesAndLoans | `open_credit_lines` |
| NumberRealEstateLoansOrLines | `real_estate_loans` |
| NumberOfDependents | `dependents` |

**Why:** More legible and better for programming langauges.


## D3: Missing MonthlyIncome

**What I found:** 29,731 of 150,000 rows (19.8%) have no income. These rows default at 5.6%, compared with 7.0% for rows that have an income, so whether income is missing is linked to the outcome. Income is right-skewed: median £5,400 vs mean £6,670.

**Options:**
1. Drop the rows.
2. Fill with the median.
3. Fill with the median and add a 0/1 flag column `income_missing`.

**Decision:** Option 3. Add the `income_missing` flag in silver. Fill the gaps with the median, worked out from the training data only (see D10).

**Why:** The rows aren't missing at random. Their default rate differs, so the fact
that income is missing is itself useful information, and the flag lets the model use
it. The median, not the mean, because income is heavily right-skewed.


## D4: Missing NumberOfDependents

**What I found:** 3,924 rows are missing dependents. All 3,924 of them also have missing income, so both gaps seem to come from the same cause. The median number of dependents is 0.

**Options:**
1. Fill with 0 (which is also the median).
2. Fill with 0 and add a separate `dependents_missing` flag.
3. Drop the rows.

**Decision:** Option 1. Fill with 0, with no extra flag, because every one of these rows is already flagged by `income_missing` (D3).

**Why:** Normal for someone to have no dependents.


## D5: The 96 and 98 codes in the late-payment columns

**What I found:** In all three late-payment columns, the real counts stop at around 13–17, then jump to exactly 96 and 98. It's the same 269 rows in all three columns. Being late 98 times in two years isn't possible, so these look like system codes ("unknown" or similar). These 269 people default at 54.6%, about eight times the normal rate, so the code means something risky.

**Options:**
1. Leave the values as they are.
2. Drop the 269 rows.
3. Add a 0/1 flag `late_code_96_98`, then set the three late counts to 0 for those rows.
4. Add the flag, then set the counts to missing and let them be filled later.

**Decision:** Option 3. Keep the information in the flag, and stop the fake counts of 96/98 from distorting the late-payment columns.

**Why:** Clearly an error, but still valuable data in the row.


## D6: Age 0

**What I found:** One person is listed as aged 0 (id 65696; pandas shows it at index 65695 because the index starts at 0). Nobody else is under 21.

**Options:**
1. Drop the row.
2. Set the age to missing and fill it with the median.

**Decision:** Option 1. Drop the row.

**Why:** Age is an important feature, guessing the age will not help the model.


## D7: RevolvingUtilization above 1

**What I found:** This should be the share of credit card limits used, normally 0 to 1. 3,321 people are above 1, 371 are above 2, 241 are above 10, and the maximum is 50,708. People between 1 and 2 default at 40%: they really are over their limits, which is a strong risk signal. People above 2 default at only 14.6%, close to normal, which suggests those values are errors rather than extreme over-spending.

**Options:**
1. Leave everything as it is.
2. Cap all values at 1.
3. Keep values up to 2 as real; treat values above 2 as errors (set them to missing, to be filled later).
4. Cap everything at the 99th percentile (about 1.09).

**Decision:** Option 3. Values from 1 to 2 are kept as genuine over-limit use; values above 2 become missing.

**Why:** Values above 2 are most likely erros, therefore should not be included, but their row is still important.


## D8: Huge DebtRatio values

**What I found:** DebtRatio should be monthly debt payments ÷ monthly income, usually under 1. The median is 0.30 for people with an income but 1,159 for people without one, and 93% of rows with DebtRatio above 100 have missing income. When there's no income to divide by, the column seems to hold the debt amount in pounds instead of a ratio. Even among people with an income there are odd values: 2,106 are above 10, and the maximum is 61,106.

**Options:**
1. Leave it.
2. Set DebtRatio to missing wherever income is missing, because it isn't a ratio there (the `income_missing` flag from D3 keeps the information).
3. Option 2, and also cap the remaining values at a fixed limit, e.g. 5 (paying out five times your income in debt every month isn't realistic).
4. Drop the column.

**Decision:** Option 3. Set it to missing where income is missing, and cap the rest at 5.

**Why:** If income is missing, cannot work out the debt ratio, therefore set it to missing rather than an incorrect value.


## D9: Rows that are identical apart from the id

**What I found:** 609 rows are exact copies of another row once the id is ignored (960 rows are involved in total). 85% of these rows have missing income, and their default rate is only 3.3%. They're mostly "sparse" profiles: no income, no late payments, few loans. People like that can easily look identical without being the same person.

**Options:**
1. Drop the copies as duplicates.
2. Keep them as different people who happen to match.

**Decision:** Option 2. Keep them.

**Why:** Very likely that these are different people. Very common data on each column.


## D10: Train/test split, and where data-driven steps happen

**What I found:** Only `cs-training.csv` has the target filled in. Kaggle's `cs-test.csv` has the target column empty, because it was for leaderboard submissions, so it can't be used to measure the model. The target is imbalanced (6.7% default).

Some cleaning steps are **fixed rules** that don't learn anything from the data (renaming, the 96/98 rule, dropping age 0, the caps in D7 and D8). Others **learn from the data** (filling gaps with a median). If a median is worked out from all the data before splitting, the test set leaks into training (chapter 11).

**Options:**
1. Do all cleaning, including the medians, in silver, then split in gold.
2. Do the fixed rules in silver. Split in the modelling step. Put the median imputation inside the model's scikit-learn Pipeline, so it's fitted on the training data only.

**Decision:** Option 2. Use an 80/20 split of `cs-training.csv`, stratified on the target, with a fixed random seed. 

**Why:** Best practice, so that the model is fitted on training data only.
