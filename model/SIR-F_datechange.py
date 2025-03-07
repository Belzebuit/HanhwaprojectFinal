import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit

# ✅ 데이터 로드
military_data = pd.read_csv("Processed_COVID_Data_Filled.csv", encoding="ISO-8859-1")
civil_data = pd.read_csv("Processed_COVID_Data_Filled_Civil_20th.csv", encoding="ISO-8859-1")

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

# ✅ 총 인구 설정 2020년 기준
N_military = 555000      # 군 총 인원 
N_civil = 7038000       # 민간사회 총 인구 

# ✅ 감염 회복 기간 & 회복률 설정 (최소 및 최대값 개별 적용)
T_recovery_military_min, T_recovery_military_max = 7, 14  # 군인의 격리 기간 7~14일
T_recovery_civil_min, T_recovery_civil_max = 5, 20        # 민간의 격리 기간 5~20일

gamma_military_min = 1 / T_recovery_military_min
gamma_military_max = 1 / T_recovery_military_max
gamma_civil_min = 1 / T_recovery_civil_min
gamma_civil_max = 1 / T_recovery_civil_max

# ✅ 감염자 수가 3명 미만이면 0으로 설정 (삭제 X)
military_cases.loc[military_cases["cases"] < 3, "cases"] = 0
civil_cases.loc[civil_cases["cases"] < 3, "cases"] = 0

# ✅ 초기 조건 설정
I0_military = military_cases[military_cases["cases"] > 0]["cases"].iloc[0]
I0_civil = civil_cases[civil_cases["cases"] > 0]["cases"].iloc[0]

R0_military = 0  # 초기 완치자 수
R0_civil = 0

S0_military = N_military - I0_military - R0_military
S0_civil = N_civil - I0_civil - R0_civil

# ✅ 시간 데이터 설정
t_military = np.arange(len(military_cases))
t_civil = np.arange(len(civil_cases))

# ✅ SIR-F 모델 정의
def sir_f(t, y, beta, gamma, N):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return [dSdt, dIdt, dRdt]

# ✅ 최적화 함수 정의
def fit_sir_f(t, beta, gamma, N, S0, I0, R0):
    sol = solve_ivp(sir_f, [t[0], t[-1]], [S0, I0, R0], args=(beta, gamma, N), t_eval=t)
    return sol.y[1]

# ✅ 최적화 실행
p0_beta = 0.2
max_nfev = 5000

def optimize_beta(gamma):
    popt_military, _ = curve_fit(
        lambda t, beta: fit_sir_f(t, beta, gamma, N_military, S0_military, I0_military, R0_military),
        t_military, military_cases["cases"], bounds=(0.001, [1]), p0=[p0_beta], max_nfev=max_nfev
    )
    popt_civil, _ = curve_fit(
        lambda t, beta: fit_sir_f(t, beta, gamma, N_civil, S0_civil, I0_civil, R0_civil),
        t_civil, civil_cases["cases"], bounds=(0.001, [1]), p0=[p0_beta], max_nfev=max_nfev
    )
    return popt_military[0], popt_civil[0]

# 최소 및 최대 격리 기간별 감염률(β) 계산
beta_military_min, beta_civil_min = optimize_beta(gamma_military_min)
beta_military_max, beta_civil_max = optimize_beta(gamma_military_max)

# ✅ 결과 출력
print(f"군대 감염률 (β) 최소: {beta_military_min:.4f}, 최대: {beta_military_max:.4f}, 회복률 (γ) 최소: {gamma_military_min:.4f}, 최대: {gamma_military_max:.4f}")
print(f"민간 감염률 (β) 최소: {beta_civil_min:.4f}, 최대: {beta_civil_max:.4f}, 회복률 (γ) 최소: {gamma_civil_min:.4f}, 최대: {gamma_civil_max:.4f}")
