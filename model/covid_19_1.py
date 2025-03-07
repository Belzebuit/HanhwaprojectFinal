import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from math import sqrt
from sklearn.metrics import mean_squared_error, mean_absolute_error

###############################################################################
# 1. ADF 검정 + 차분 (필요 시)
###############################################################################
def check_stationarity_and_diff(series, alpha=0.05, max_diff=2):
    """
    - series: 1차원 시계열(pd.Series)
    - alpha: ADF 테스트 유의수준(기본 0.05)
    - max_diff: 최대 몇 번 차분 시도할지
    - return: (시계열, 최종 차분 횟수)
    """
    # 0) 복사
    ts = series.copy()

    diff_count = 0
    for d in range(max_diff+1):
        # ADF
        test_res = adfuller(ts.dropna(), autolag='AIC')
        pval = test_res[1]
        if pval < alpha:
            print(f"  -> ADF p={pval:.4f}, d={diff_count} -> 정상성 OK")
            return ts, diff_count
        else:
            if diff_count < max_diff:
                print(f"  -> ADF p={pval:.4f} (>= {alpha}), 차분(d={diff_count+1}) 시도")
                ts = ts.diff(1).dropna()
                diff_count += 1
            else:
                print(f"  -> ADF p={pval:.4f}, 더 이상 차분 불가(max_diff={max_diff}). 비정상 가능성")
                return ts, diff_count

    return ts, diff_count


###############################################################################
# 2. SARIMAX Rolling Forecast
###############################################################################
def rolling_sarimax_forecast(endog, exog=None,
                             order=(1,0,1),
                             seasonal_order=(0,0,0,0),
                             test_size=10,
                             freq='D'):
    """
    [역할]
      - (endog, exog) 시계열을 주고, SARIMAX로 rolling forecast(1-step ahead) 하는 예시
      - test_size: 뒤쪽 test_size개를 한 스텝씩 예측

    [핵심 포인트: exog 데이터 처리]
      - get_forecast(steps=1, exogenous=…) 할 때,
        예측할 날짜 인덱스와 같은 (1 x n_features) DataFrame을 만들어야 Out-of-Sample 오류 안 남

    [리턴] (df_res, final_model)
      - df_res: (actual, pred)
      - final_model: 마지막 시점의 fitted model 결과
    """
    # 0) train/test 분할
    n = len(endog)
    train_n = n - test_size
    train_endog = endog.iloc[:train_n]
    test_endog  = endog.iloc[train_n:]

    if exog is not None:
        train_exog = exog.iloc[:train_n, :]
        test_exog  = exog.iloc[train_n:, :]
    else:
        train_exog = None
        test_exog  = None

    print("\n=== Rolling SARIMAX Forecast ===")
    print(f" train_n={train_n}, test_n={test_size}")
    print(f" order={order}, seasonal_order={seasonal_order}")

    # 1) 초기 모델 피팅
    model = sm.tsa.statespace.SARIMAX(
        train_endog,
        exog=train_exog,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    results = model.fit(disp=False)
    print("\n[Initial SARIMAX fit]")
    print(results.summary())

    # 2) 롤링 예측
    preds = []
    actuals = []
    current_results = results

    for i in range(len(test_endog)):
        this_date = test_endog.index[i]
        y_true = test_endog.iloc[i]

        # exog 준비
        if test_exog is not None:
            # shape=(1, n_features)
            x_row = test_exog.iloc[[i]]       # i:i+1
            # 인덱스를 예측할 날짜로!
            x_row.index = [this_date]
        else:
            x_row = None

        # (A) 1-step 예측
        #     get_forecast(1, exogenous= x_row)
        # fc = current_results.get_forecast(steps=1, exogenous=x_row)
        # y_pred = fc.predicted_mean.iloc[0]
        fc_val = current_results.predict(
            start=current_results.nobs, 
            end=current_results.nobs, 
            exog=x_row
        )
        y_pred = fc_val.iloc[0]

        preds.append(y_pred)
        actuals.append(y_true)

        # (B) 모델 상태 업데이트(append)
        current_results = current_results.append(
            endog=[y_true],
            exog=x_row,
            refit=False
        )

    df_res = pd.DataFrame({'actual': actuals, 'pred': preds}, index=test_endog.index)

    # RMSE, MAE
    rmse_ = sqrt(mean_squared_error(df_res['actual'], df_res['pred']))
    mae_  = mean_absolute_error(df_res['actual'], df_res['pred'])

    print("\n=== [Rolling Forecast Result] ===")
    print(df_res)
    print(f"RMSE={rmse_:.3f}, MAE={mae_:.3f}")

    # 시각화
    plt.figure(figsize=(10,4))
    plt.plot(train_endog.index, train_endog, label='Train')
    plt.plot(test_endog.index, test_endog, label='Test Actual')
    plt.plot(df_res.index, df_res['pred'], label='Test Pred', marker='x')
    plt.title(f"SARIMAX Rolling - RMSE={rmse_:.3f}, MAE={mae_:.3f}")
    plt.legend()
    plt.grid()
    plt.show()

    return df_res, current_results


###############################################################################
# 3. 전체 실행 예시
###############################################################################
if __name__ == "__main__":

    # (A) 데이터 불러오기
    #  - 이미 질문에 주신 csv 내용 그대로라면, pandas로 읽어온 뒤,
    #    'Date'로 set_index 하시면 됩니다.
    #  - 여기서는 가정: df = pd.read_csv('your_data.csv', parse_dates=['Date'], index_col='Date')
    #    ... 사용자 환경에 맞춰 조정!
    print("\n[Load CSV to df ...]")
    df = pd.read_csv('Processed_COVID_Data_Filled.csv', parse_dates=['Date'], index_col='Date', encoding='ANSI')
    df.sort_index(inplace=True)
    print(df.head())
    print(df.tail())

    # (B) 타겟 / exog 정의
    #  - 'Cases'를 예측 (endog)
    #  - 나머지 컬럼(SO2, CO, O3, ...)을 exog로
    target_col = 'Cases'
    # 가능한 exog 목록에서 'Cases' 제외
    exog_cols = [c for c in df.columns if c != target_col]

    # (C) ADF & 차분
    # endog
    print("\n[ADF & diff] for Cases:")
    y_raw = df[target_col].astype(float)
    y_sta, dcount = check_stationarity_and_diff(y_raw, alpha=0.05, max_diff=2)

    # exog: 여기서는 따로 차분하지 않음(필요하다면 diff)
    X_exog = df[exog_cols].astype(float)
    if dcount>0:
        # 만약 endog를 dcount번 차분했다면,
        # exog도 동일 차분하는 게 보통이지만, 일단 여기서는 생략/혹은 선택
        # ex) X_exog = X_exog.diff(dcount).dropna()
        #     그리고 y_sta.index와 맞춰주기
        X_exog = X_exog.loc[y_sta.index]

    # (D) train/test 분할 크기
    #  - 끝에서 10일을 test
    #  - 질문에 따라 조절
    test_size = 10

    # (E) Rolling SARIMAX 실행
    #  - order, seasonal_order를 ACF/PACF로 추정하거나, AutoARIMA 등으로 찾아도 됨
    #  - 여기서는 (1, dcount, 1) 시도
    order_ = (1, dcount, 1)
    seas_  = (0,0,0,0)

    df_out, final_model = rolling_sarimax_forecast(
        endog=y_sta,
        exog=X_exog,
        order=order_,
        seasonal_order=seas_,
        test_size=test_size
    )

    # (F) 잔차 분석
    resid = final_model.resid
    plt.figure(figsize=(12,4))
    plt.subplot(1,2,1)
    sm.qqplot(resid, line='45', ax=plt.gca())
    plt.title("Q-Q Plot (Resid)")
    plt.subplot(1,2,2)
    plot_acf(resid.dropna(), lags=20, ax=plt.gca())
    plt.show()

    # (G) 최종 요약
    rmse_ = sqrt(mean_squared_error(df_out['actual'], df_out['pred']))
    mae_  = mean_absolute_error(df_out['actual'], df_out['pred'])
    print(f"\n[Done] Rolling SARIMAX => RMSE={rmse_:.4f}, MAE={mae_:.4f}")