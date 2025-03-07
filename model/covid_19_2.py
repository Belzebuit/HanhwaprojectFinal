
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
from math import sqrt
from sklearn.metrics import mean_squared_error, mean_absolute_error

###############################################################################
# 1. ADF 검정 + 차분 (필요 시)
###############################################################################
def check_stationarity_and_diff(series, alpha=0.05, max_diff=2):
    ts = series.copy()
    diff_count = 0
    for d in range(max_diff + 1):
        test_res = adfuller(ts.dropna(), autolag='AIC')
        pval = test_res[1]
        if pval < alpha:
            return ts, diff_count
        else:
            if diff_count < max_diff:
                ts = ts.diff(1).dropna()
                diff_count += 1
            else:
                return ts, diff_count
    return ts, diff_count

###############################################################################
# 2. SARIMAX Rolling Forecast
###############################################################################
def rolling_sarimax_forecast(endog, exog=None, order=(1, 0, 1), seasonal_order=(0, 0, 0, 0), test_size=10):
    n = len(endog)
    train_n = n - test_size
    train_endog = endog.iloc[:train_n]
    test_endog = endog.iloc[train_n:]
    train_exog = exog.iloc[:train_n, :] if exog is not None else None
    test_exog = exog.iloc[train_n:, :] if exog is not None else None

    model = sm.tsa.statespace.SARIMAX(
        train_endog,
        exog=train_exog,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    results = model.fit(disp=False)

    preds = []
    actuals = []
    current_results = results

    for i in range(len(test_endog)):
        this_date = test_endog.index[i]
        y_true = test_endog.iloc[i]
        x_row = test_exog.iloc[[i]] if test_exog is not None else None
        if x_row is not None:
            x_row.index = [this_date]
        fc_val = current_results.predict(
            start=current_results.nobs,
            end=current_results.nobs,
            exog=x_row
        )
        y_pred = max(fc_val.iloc[0], 0)
        preds.append(y_pred)
        actuals.append(y_true)
        current_results = current_results.append(endog=[y_true], exog=x_row, refit=False)

    df_res = pd.DataFrame({'actual': actuals, 'pred': preds}, index=test_endog.index)
    rmse_ = sqrt(mean_squared_error(df_res['actual'], df_res['pred']))
    mae_ = mean_absolute_error(df_res['actual'], df_res['pred'])
    return df_res, current_results, train_endog, rmse_, mae_

###############################################################################
# 3. 전체 실행 예시
###############################################################################
if __name__ == "__main__":
    df = pd.read_csv('Processed_COVID_Data_Filled.csv', parse_dates=['Date'], index_col='Date', encoding='ANSI')
    df.sort_index(inplace=True)
    target_col = 'Cases'
    exog_cols = [c for c in df.columns if c != target_col]
    df[target_col] = np.log1p(df[target_col])

    for col in exog_cols:
        min_val = df[col].min()
        shift = abs(min_val) + 1e-5 if min_val <= 0 else 0
        df[col] = np.log1p(df[col] + shift)

    y_raw = df[target_col].astype(float)
    y_sta, dcount = check_stationarity_and_diff(y_raw, alpha=0.05, max_diff=2)
    X_exog = df[exog_cols].loc[y_sta.index]

    test_size = 10
    order_ = (1, dcount, 1)
    seas_ = (0, 0, 0, 0)
    df_out, final_model, train_endog, rmse_, mae_ = rolling_sarimax_forecast(
        endog=y_sta, exog=X_exog, order=order_, seasonal_order=seas_, test_size=test_size
    )

    df_out['actual_exp'] = np.expm1(df_out['actual'])
    df_out['pred_exp'] = np.expm1(df_out['pred'])

    plt.figure(figsize=(12, 6))
    plt.plot(train_endog, label="Train Data (Log Scale)", color='blue')
    plt.plot(df_out.index, df_out['actual'], label="Test Actual (Log Scale)", color='orange')
    plt.plot(df_out.index, df_out['pred'], label="Test Predicted (Log Scale)", linestyle='--', color='green', marker='x')
    plt.legend()
    plt.title(f"SARIMAX Rolling (Log Scale) - RMSE={rmse_:.3f}, MAE={mae_:.3f}")
    plt.grid()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(train_endog.index, np.expm1(train_endog), label="Train Data (Original Scale)", color='blue')
    plt.plot(df_out.index, df_out['actual_exp'], label="Test Actual (Original Scale)", color='orange')
    plt.plot(df_out.index, df_out['pred_exp'], label="Test Predicted (Original Scale)", linestyle='--', color='green', marker='x')
    plt.legend()
    plt.title(f"SARIMAX Rolling (Original Scale) - RMSE={rmse_:.3f}, MAE={mae_:.3f}")
    plt.grid()
    plt.show()

    resid = final_model.resid
    plt.figure(figsize=(12, 4))
    sm.qqplot(resid, line='45', ax=plt.subplot(1, 2, 1))
    plt.title("Q-Q Plot (Resid)")
    plot_acf(resid.dropna(), lags=20, ax=plt.subplot(1, 2, 2))
    plt.title("Autocorrelation (Resid)")
    plt.tight_layout()
    plt.show()
