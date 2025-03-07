import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import requests
import io

# API 요청 설정
domain = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php?"
tm1 = "tm1=20240101&"
tm2 = "tm2=20241231&"
stn_id = "stn=0&"
option = "help=0&authKey="
auth = "IKekZYDNQQOnpGWAzaED9A"  # 부여받은 API Key 입력
url = domain + tm1 + tm2 + stn_id + option + auth

# 지점번호와 지점명 매핑
station_mapping = {
    90: "속초", 93: "북춘천", 95: "철원", 98: "동두천", 99: "파주", 
    100: "대관령", 101: "춘천", 102: "백령도", 104: "북강릉", 105: "강릉", 
    106: "동해", 108: "서울", 112: "인천", 114: "원주", 115: "울릉도", 
    119: "수원", 121: "영월", 127: "충주", 129: "서산", 130: "울진", 
    131: "청주", 133: "대전", 135: "추풍령", 136: "안동", 137: "상주", 
    138: "포항", 140: "군산", 143: "대구", 146: "전주", 152: "울산", 
    155: "창원", 156: "광주", 159: "부산", 162: "통영", 165: "목포", 
    168: "여수", 169: "흑산도", 170: "완도", 172: "고창", 174: "순천", 
    175: "고산", 177: "홍성", 181: "서청주", 184: "제주", 185: "고산(제주)", 
    188: "성산", 189: "서귀포", 192: "진주", 201: "강화", 202: "양평", 
    203: "이천", 211: "인제", 212: "홍천", 216: "태백", 217: "정선군", 
    221: "제천", 226: "보은", 232: "천안", 235: "보령", 236: "부여", 
    238: "금산", 239: "세종", 243: "부안", 244: "임실", 245: "정읍", 
    247: "남원", 248: "장수", 251: "고창군", 252: "영광군", 253: "김해시", 
    254: "순창군", 255: "북창원", 256: "해남군", 257: "양산시", 258: "보성군", 
    259: "강진군", 260: "장흥", 261: "해남", 262: "고흥", 263: "의령군", 
    264: "함양군", 266: "광양시", 268: "진도군", 271: "봉화", 272: "영주", 
    273: "문경", 276: "청송군", 277: "영덕", 278: "의성", 279: "구미", 
    281: "영천", 283: "경주시", 284: "거창", 285: "합천", 288: "밀양", 
    289: "산청", 294: "거제", 295: "남해", 296: "북부산"
}



# API 요청
response = requests.get(url)

if response.status_code == 200:
    # 응답 데이터를 EUC-KR로 디코딩
    raw_data = response.content.decode('euc-kr')
    
    # 데이터 로드 (헤더 없는 상태로 로드)
    df = pd.read_csv(io.StringIO(raw_data), skiprows=5, delim_whitespace=True, header=None)

    # 열 이름 수동 설정
    df.columns = [
        "TM", "STN", "WS_AVG", "WR_DAY", "WD_MAX", "WS_MAX", "WS_MAX_TM", "WD_INS", "WS_INS", "WS_INS_TM",
        "TA_AVG", "TA_MAX", "TA_MAX_TM", "TA_MIN", "TA_MIN_TM", "TD_AVG", "TS_AVG", "TG_MIN", "HM_AVG", 
        "HM_MIN", "HM_MIN_TM", "PV_AVG", "EV_S", "EV_L", "FG_DUR", "PA_AVG", "PS_AVG", "PS_MAX", "PS_MAX_TM", 
        "PS_MIN", "PS_MIN_TM", "CA_TOT", "SS_DAY", "SS_DUR", "SS_CMB", "SI_DAY", "SI_60M_MAX", "SI_60M_MAX_TM", "RN_DAY", 
        "RN_D99", "RN_DUR", "RN_60M_MAX", "RN_60M_MAX_TM", "RN_10M_MAX", "RN_10M_MAX_TM", "RN_POW_MAX", "RN_POW_MAX_TM", 
        "SD_NEW", "SD_NEW_TM", "SD_MAX", "SD_MAX_TM", "TE_05", "TE_10", "TE_15", "TE_30", "TE_50"
    ][:len(df.columns)]  # 실제 열 개수만큼 자르기
    
    # NaN 값 확인 및 처리
    if df["STN"].isnull().any():
        print("STN 열에 NaN 값이 존재합니다. NaN 값을 '미확인'으로 처리합니다.")
    
    # 지점번호를 지점명으로 변환 (NaN 값은 "미확인"으로 처리)
    df["STN"] = df["STN"].apply(lambda x: station_mapping.get(int(x), "미확인") if pd.notnull(x) else "미확인")
    
    # 열 이름 변경
    df.rename(columns={
        "TM": "관측시각 (KST)",
        "STN": "국내 지점번호",
        "TA_MAX": "최고기온 (C)",
        "TA_MIN": "최저기온 (C)",
        "TA_AVG": "일 평균기온 (C)",
        "WS_AVG": "일 평균 풍속 (m/s)",
        "RN_DAY": "일강수량 (mm)",
        "SD_NEW": "최심 신적설 (cm)",
        "HM_AVG": "일 평균 상대습도 (%)"
    }, inplace=True)
    
    # "일교차 (C)" 추가
    df["일교차 (C)"] = df["최고기온 (C)"] - df["최저기온 (C)"]
    
    # 필요한 열만 선택
    selected_columns = [
        "관측시각 (KST)", "국내 지점번호", "최고기온 (C)", "최저기온 (C)", 
        "일 평균기온 (C)", "일 평균 풍속 (m/s)", "일강수량 (mm)", 
        "최심 신적설 (cm)", "일 평균 상대습도 (%)", "일교차 (C)"
    ]
    selected_df = df[selected_columns]
    
    # 데이터 검증
    print("선택된 데이터:")
    print(selected_df.head())  # 선택된 데이터프레임 첫 5개 행 출력
    
    # 데이터 CSV로 저장
    output_file = "2024weather.csv"
    selected_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"선택된 데이터가 '{output_file}' 파일로 저장되었습니다.")
else:
    print(f"API 요청 실패: 상태 코드 {response.status_code}")
