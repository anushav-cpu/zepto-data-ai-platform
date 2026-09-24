# Module 2 — Analytics Pipeline

## Overview

This module performs exploratory data analysis, classification modeling, class-imbalance analysis, hyperparameter tuning, and fare regression using the classic Titanic dataset.

The Titanic dataset was loaded once using `seaborn.load_dataset("titanic")` in `01_eda.ipynb` and immediately saved as `titanic.csv`. The modeling notebook reads this shared CSV file.

---

## Part A — Exploratory Data Analysis

### Task 1 — Load and Profile

The Titanic dataset contains:

* Rows: **891**
* Columns: **15**

The dataset was profiled using `df.info()`, `df.describe()`, and `df.shape`.

The original dataset was saved immediately after loading as:

```text
titanic.csv
```

### Task 2 — Missing-Value Handling

The original dataset contained missing values in four columns.

| Column      | Missing Count | Missing Percentage | Handling                                     |
| ----------- | ------------: | -----------------: | -------------------------------------------- |
| age         |           177 |           19.8653% | Median imputation                            |
| embarked    |             2 |            0.2245% | Drop affected rows                           |
| deck        |           688 |           77.2166% | Drop column because of very high missingness |
| embark_town |             2 |            0.2245% | Dropped as redundant with `embarked`         |

The `age` column was imputed using its median because its missing percentage was between 5% and 30%.

The two rows with missing `embarked` values were removed because the missing percentage was below 5%.

The `deck` column had more than 77% missing values, so it was removed because reliable imputation would not be appropriate.

The `embark_town` column was removed because it duplicates the embarkation information represented by `embarked`.

After missing-value handling, no missing values remained in the cleaned EDA dataset.

---

## Task 3 — Univariate Analysis

### Age

Age was analyzed using a histogram and boxplot.

Using the IQR method:

* Age outliers: **65**

### Fare

Fare was analyzed using a histogram and boxplot.

Using the IQR method:

* Fare outliers: **114**

Fare statistics:

| Statistic |   Value |
| --------- | ------: |
| Mean      | 32.0967 |
| Median    | 14.4542 |
| Mode      |    8.05 |
| Skewness  |  4.8014 |

The fare distribution is **right-skewed** because the mean is greater than the median, which is greater than the mode. The high positive skewness also confirms a strong right tail caused by relatively high fares.

---

## Task 4 — Bivariate Analysis

### Survival Rate by Sex

* Male survival rate: **18.89%**
* Female survival rate: **74.04%**

Female passengers had a substantially higher observed survival rate than male passengers in this dataset.

### Survival Rate by Passenger Class

* 1st class: **62.62%**
* 2nd class: **47.28%**
* 3rd class: **24.24%**

The observed survival rate decreased across the passenger classes from 1st to 3rd class.

### Survival Rate by Sex and Passenger Class

| Group             | Survival Rate |
| ----------------- | ------------: |
| Male, 1st Class   |        36.89% |
| Male, 2nd Class   |        15.74% |
| Male, 3rd Class   |        13.54% |
| Female, 1st Class |        96.74% |
| Female, 2nd Class |        92.11% |
| Female, 3rd Class |        50.00% |

Boolean masking using `&` was used to calculate the combined sex and passenger-class survival rates.

### Correlation Analysis

The correlation analysis used exactly these six columns:

```text
survived
pclass
age
sibsp
parch
fare
```

The boolean columns `adult_male` and `alone` were excluded.

The two strongest absolute off-diagonal correlations were:

1. **pclass vs fare: -0.548**
2. **sibsp vs parch: 0.415**

The negative correlation between `pclass` and `fare` indicates that higher passenger-class status, represented by a lower numerical `pclass` value, was generally associated with higher fares.

The positive correlation between `sibsp` and `parch` indicates that passengers with more siblings/spouses also tended to have more parents/children, reflecting family-group structure in the dataset.

A correlation heatmap was created using the six specified columns.

---

## Task 5 — Multivariate Data Story

Four charts were created to examine survival using multiple variables.

### 1. Survival Rate by Sex and Passenger Class

Survival rates varied substantially by both sex and passenger class. Female passengers had higher survival rates than male passengers across the passenger classes, while first-class passengers generally had higher survival rates than passengers in lower classes. This shows that both sex and passenger class were important factors associated with survival.

### 2. Survival Rate by Age Group and Sex

Survival rates differed across age groups and between males and females. Female passengers generally showed higher survival rates than males within the same age groups, although the pattern varies across groups. The chart helps show how age and sex together were associated with survival outcomes.

### 3. Fare Distribution by Passenger Class and Survival

Fare levels differed strongly across passenger classes, with higher fares generally associated with higher passenger classes. Within each class, fare distributions also varied between survivors and non-survivors. This suggests that economic position, represented by fare and class, was related to the survival outcome.

### 4. Survival Rate by Family Size and Passenger Class

Survival rates varied with family size and passenger class. The relationship between family size and survival was not uniform across all passenger classes, indicating that class influenced the observed survival pattern. Very small and very large family groups can show different survival outcomes.

---

## Task 6 — Exploratory Standardization

Age and fare were standardized using z-scores with `StandardScaler`.

The resulting means were approximately **0**, and the standard deviations were approximately **1**.

Observed results:

| Feature | Standardized Mean | Standardized Std |
| ------- | ----------------: | ---------------: |
| Age     |            0.0000 |           1.0006 |
| Fare    |            0.0000 |           1.0006 |

This standardization was performed as an EDA sanity check only and was not used as modeling preprocessing.

---

# Part B — Modeling

## Task 7 — Stratified Train/Test Split

The dataset was divided into:

* **80% training data**
* **20% test data**
* `random_state=42`
* `stratify=y`

Stratification was used because the survival classes are imbalanced. It helps preserve similar class proportions in the training and test sets.

The split was performed before model preprocessing.

---

## Task 8 — Train-Only Preprocessing

A `ColumnTransformer` and `Pipeline` were used for preprocessing.

Numeric features:

```text
pclass
age
sibsp
parch
fare
```

Categorical features:

```text
sex
embarked
```

Numeric preprocessing used median imputation followed by `StandardScaler`.

Categorical preprocessing used most-frequent imputation followed by one-hot encoding.

All preprocessing steps were fitted only on training data through the modeling pipelines. Test data was transformed using the fitted training preprocessing.

---

## Task 9 — Classification Models

Three classifiers were trained using the same stratified train/test split:

1. Logistic Regression
2. Decision Tree
3. Random Forest

The Decision Tree was visualized using `plot_tree`, including feature names and class names.

---

## Task 10 — Classification Evaluation

The classifiers were evaluated using:

* Accuracy
* Precision
* Recall
* F1 score
* ROC-AUC
* Confusion matrix
* ROC curve

### Classification Comparison

| Model               | Accuracy | Precision | Recall |     F1 |    AUC |
| ------------------- | -------: | --------: | -----: | -----: | -----: |
| Logistic Regression |   0.8045 |    0.7931 | 0.6667 | 0.7244 | 0.8437 |
| Decision Tree       |   0.7933 |    0.8636 | 0.5507 | 0.6726 | 0.8292 |
| Random Forest       |   0.8156 |    0.8000 | 0.6957 | 0.7442 | 0.8287 |
| Tuned Random Forest |   0.8156 |    0.8750 | 0.6087 | 0.7179 | 0.8431 |

Confusion matrices and combined ROC curves were saved in the `charts` folder.

---

## Task 11 — Class Imbalance

The survival classes were imbalanced, with more passengers not surviving than surviving.

Three Logistic Regression approaches were compared:

1. Baseline
2. `class_weight="balanced"`
3. SMOTE applied only to the training data

### Imbalance Comparison

| Approach         | Precision | Recall |     F1 |
| ---------------- | --------: | -----: | -----: |
| Baseline         |    0.7931 | 0.6667 | 0.7244 |
| Balanced Weights |    0.7297 | 0.7826 | 0.7552 |
| SMOTE            |    0.7397 | 0.7826 | 0.7606 |

In this experiment, SMOTE produced the highest F1 score of **0.7606** among the three imbalance-handling approaches. It achieved a recall of **0.7826** and precision of **0.7397**. The result indicates that SMOTE improved the balance between precision and recall for this test set.

SMOTE was applied only after the training data entered the preprocessing pipeline, so the test set was not oversampled.

---

## Task 12 — Random Forest Hyperparameter Tuning

`GridSearchCV` with five-fold cross-validation was used to tune the Random Forest.

The searched parameters were:

```text
n_estimators: [100, 200]
max_depth: [5, 10, None]
max_features: ["sqrt", "log2"]
```

F1 score was used as the GridSearchCV scoring metric.

### Best Parameters

```text
max_depth = 5
max_features = sqrt
n_estimators = 100
```

* Best cross-validation F1: **0.7459**
* OOB score: **0.8272**

Tuned Random Forest test performance:

* Accuracy: **0.8156**
* Precision: **0.8750**
* Recall: **0.6087**
* F1: **0.7179**
* AUC: **0.8431**

The Random Forest estimator was created with `oob_score=True` and `bootstrap=True`, allowing the OOB score to be reported.

---

## Task 13 — Fare Regression

A multivariate Linear Regression model was used to predict `fare` from other available features.

Predictor variables included:

```text
pclass
sex
age
sibsp
parch
embarked
```

Regression metrics:

| Metric      |   Value |
| ----------- | ------: |
| MAE         | 20.8094 |
| RMSE        | 30.4731 |
| R²          |  0.3999 |
| Adjusted R² |  0.3679 |

The residual analysis showed that the residual spread changed noticeably across predicted fare levels, suggesting **heteroscedasticity**.

Classification metrics and regression metrics are reported separately because they measure different types of model performance and are not directly comparable.

---

## Task 14 — Final Model Comparison and Recommendation

Based on the held-out test set, the standard Random Forest had the highest F1 score (**0.7442**) and accuracy (**0.8156**) among the evaluated classifiers. Its precision was **0.8000**, recall was **0.6957**, and AUC was **0.8287**. The tuned Random Forest improved precision to **0.8750** and achieved an AUC of **0.8431**, but its recall (**0.6087**) and F1 (**0.7179**) were lower. Therefore, the standard Random Forest was selected as the final pipeline in this experiment because F1 was used as the primary selection criterion; business costs associated with false positives and false negatives should also be considered before deployment.

The regression model was evaluated separately using MAE, RMSE, R², and Adjusted R².

---

## Task 15 — Saved Complete Pipeline

The selected Random Forest pipeline was saved as a complete pipeline containing preprocessing and the final estimator.

Saved file:

```text
model/titanic_best_pipeline.joblib
```

The saved pipeline was reloaded using `joblib.load()` and tested with raw passenger input.

The successful prediction confirmed that the complete saved pipeline can process raw input and generate predictions.

---

## Module 2 Files

```text
analytics/
├── 01_eda.ipynb
├── 02_modeling.ipynb
├── titanic.csv
├── correlation_results.txt
├── regression_results.csv
├── regression_interpretation.txt
├── charts/
│   ├── confusion_matrices.png
│   ├── decision_tree.png
│   ├── fare_by_class_survival.png
│   ├── fare_residual_plot.png
│   ├── roc_curves.png
│   ├── survival_by_age_group_sex.png
│   ├── survival_by_family_size_class.png
│   └── survival_by_sex_class.png
├── model/
│   └── titanic_best_pipeline.joblib
└── README.md
```

## Conclusion

Module 2 covers exploratory analysis, missing-value handling, visualization, correlation analysis, standardization, stratified classification, train-only preprocessing, class-imbalance handling, Random Forest tuning, regression analysis, model comparison, and saving a reloadable complete ML pipeline.
