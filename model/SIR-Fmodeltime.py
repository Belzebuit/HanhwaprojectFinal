import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ✅ 데이터 로드
military_data = pd.read_csv("Processed_COVID_Data_Filled.csv", encoding="ISO-8859-1")
civil_data = pd.read_csv("Processed_COVID_Data_Filled_Civil.csv", encoding="ISO-8859-1")

# ✅ 날짜 변환
military_data.rename(columns={"Date": "date", "Cases": "cases"}, inplace=True)
civil_data.rename(columns={"Date": "date", "Cases": "cases"}, inplace=True)

military_data["date"] = pd.to_datetime(military_data["date"])
civil_data["date"] = pd.to_datetime(civil_data["date"])

# ✅ 일일 확진자 수 추출 & 데이터 정수 변환
military_cases = military_data[["date", "cases"]].set_index("date")
civil_cases = civil_data[["date", "cases"]].set_index("date")

military_cases["cases"] = military_cases["cases"].astype(str).str.replace(",", "").str.strip().astype(int)
civil_cases["cases"] = civil_cases["cases"].astype(str).str.replace(",", "").str.strip().astype(int)

# ✅ 감염 회복률 설정
T_recovery_military = 10  # 군: 10일
T_recovery_civil = 7      # 민간: 7일

gamma_military = 1 / T_recovery_military
gamma_civil = 1 / T_recovery_civil

# ✅ 감염률 변화 계산 함수 (감염자 수 작을 때 0 처리)
def compute_beta(cases, gamma, window_size=7, min_infected=3):
    """ 감염률 β 계산 (감염자 수 작으면 0으로 설정) """
    cases_diff = cases.diff().fillna(0)  # 일일 감염자 증가량 (dI/dt)
    beta_values = (cases_diff + gamma * cases) / cases.replace(0, np.nan)  # 감염률 계산

    # 감염자 수가 너무 작으면 감염률 0으로 설정
    beta_values[cases < min_infected] = 0

    # 음수 값 방지 (최소 0으로 설정)
    beta_values = beta_values.apply(lambda x: max(x, 0) if pd.notna(x) else x)

    # 이동 평균 적용 (급격한 변동 완화)
    beta_values = beta_values.rolling(window=window_size, min_periods=1).mean()

    return beta_values

# ✅ 각 시점의 감염률 계산 (7일 이동 평균)
military_cases["beta"] = compute_beta(military_cases["cases"], gamma_military, window_size=7)
civil_cases["beta"] = compute_beta(civil_cases["cases"], gamma_civil, window_size=7)

# ✅ 감염률 변화 그래프
plt.figure(figsize=(12, 6))
plt.plot(military_cases.index, military_cases["beta"], label="Military (β)", color="blue")
plt.plot(civil_cases.index, civil_cases["beta"], label="Civil (β)", color="red")
plt.xlabel("Date")
plt.ylabel("Estimated β (Infection Rate)")
plt.title("Time-Dependent Infection Rate (β) in Military vs. Civil Population")
plt.legend()
plt.grid()
plt.show()
