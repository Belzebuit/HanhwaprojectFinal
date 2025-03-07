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

# ✅ 감염 회복 기간 & 회복률 설정 (7일)
T_recovery_military = 10  
T_recovery_civil = 10       

gamma_military = 1 / T_recovery_military
gamma_civil = 1 / T_recovery_civil

# ✅ 감염자 수가 3명 미만이면 0으로 설정 (삭제 X)
military_cases.loc[military_cases["cases"] < 3, "cases"] = 0
civil_cases.loc[civil_cases["cases"] < 3, "cases"] = 0

# ✅ 초기 조건 설정 (감염자 초기값을 0이 아닌 첫 번째 값으로 설정)
I0_military = military_cases[military_cases["cases"] > 0]["cases"].iloc[0]
I0_civil = civil_cases[civil_cases["cases"] > 0]["cases"].iloc[0]

R0_military = 0  # 초기 완치자 수
R0_civil = 0

S0_military = N_military - I0_military - R0_military
S0_civil = N_civil - I0_civil - R0_civil

# ✅ 시간 데이터는 원래 전체 길이 유지
t_military = np.arange(len(military_cases))
t_civil = np.arange(len(civil_cases))

# ✅ SIR-F 모델 정의
def sir_f(t, y, beta, gamma, N):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return [dSdt, dIdt, dRdt]

# ✅ 최적화 함수 정의 (감염률 β 찾기) 
def fit_sir_f(t, beta, gamma, N, S0, I0, R0):
    """ 감염률 최적화 함수 """
    sol = solve_ivp(sir_f, [t[0], t[-1]], [S0, I0, R0], args=(beta, gamma, N), t_eval=t)
    return sol.y[1]  # 감염자 수 반환

# ✅ 최적화 실행 (β 찾기, 최소값 0.001 이상 설정)
p0_beta = 0.2  # 초기 감염률 추정값
max_nfev = 5000  # 최대 반복 횟수 증가

# 군 데이터 피팅
popt_military, _ = curve_fit(
    lambda t, beta: fit_sir_f(t, beta, gamma_military, N_military, S0_military, I0_military, R0_military),
    t_military, military_cases["cases"], bounds=(0.001, [1]), p0=[p0_beta], max_nfev=max_nfev
)
beta_military = popt_military[0]

# 민간 데이터 피팅
popt_civil, _ = curve_fit(
    lambda t, beta: fit_sir_f(t, beta, gamma_civil, N_civil, S0_civil, I0_civil, R0_civil),
    t_civil, civil_cases["cases"], bounds=(0.001, [1]), p0=[p0_beta], max_nfev=max_nfev
)
beta_civil = popt_civil[0]

# ✅ 그래프 출력
plt.figure(figsize=(12, 6))

plt.plot(t_civil, fit_sir_f(t_civil, beta_civil, gamma_civil, N_civil, S0_civil, I0_civil, R0_civil), 
         label="Civil (Predicted)", linestyle="dashed", color="red")
plt.scatter(t_civil, civil_cases["cases"], label="Civil (Actual)", color="orange", s=5)

plt.plot(t_military, fit_sir_f(t_military, beta_military, gamma_military, N_military, S0_military, I0_military, R0_military), 
         label="Military (Predicted)", linestyle="dashed", color="blue")
plt.scatter(t_military, military_cases["cases"], label="Military (Actual)", color="green", s=5)

plt.xlabel("Days Since First Case")
plt.ylabel("Daily Cases")
plt.title("SIR-F Model: Military vs Civil COVID-19 Spread")
plt.legend()
plt.grid()
plt.show()

# ✅ 결과 출력
print(f"군대 감염률 (β): {beta_military:.4f}, 회복률 (γ): {gamma_military:.4f}")
print(f"민간 감염률 (β): {beta_civil:.4f}, 회복률 (γ): {gamma_civil:.4f}")
