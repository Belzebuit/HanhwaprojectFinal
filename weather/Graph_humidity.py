import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 한글 폰트 설정 (환경에 맞게 수정)
font_path = 'C:/Windows/Fonts/malgun.ttf'  # Windows 예제
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

# 1. CSV 파일 불러오기
file_path = './12-24weather.csv'  # 실제 파일 경로
weather_data = pd.read_csv(file_path, encoding='cp949')

# 2. 관측시각에서 연도와 분기 추출
weather_data['연도'] = weather_data['관측시각 (KST)'].astype(str).str[:4]
weather_data['월'] = weather_data['관측시각 (KST)'].astype(str).str[4:6].astype(int)
weather_data['분기'] = (weather_data['월'] - 1) // 3 + 1  # 분기 계산
weather_data['연도_분기'] = weather_data['연도'] + '-' + weather_data['분기'].astype(str) + '분기'

# 3. 연간 평균 상대습도 시각화 (한국 전체)
annual_avg = weather_data.groupby('연도')['일 평균 상대습도 (%)'].mean().round(1)

plt.figure(figsize=(12, 6))
plt.plot(annual_avg.index, annual_avg.values, marker='o', color='#3498DB', label='연간 평균 상대습도')
plt.title('한국 연간 평균 상대습도', fontsize=16)
plt.xlabel('연도', fontsize=12)
plt.ylabel('상대습도 (%)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

# 4. 분기별 평균 상대습도 시각화 (한국 전체)
quarterly_avg = weather_data.groupby('연도_분기')['일 평균 상대습도 (%)'].mean().round(1)

# x축 레이블 커스텀: 각 해의 1분기만 표시
x_ticks = quarterly_avg.index
x_labels = [tick if '1분기' in tick else '' for tick in x_ticks]

plt.figure(figsize=(12, 6))
plt.plot(quarterly_avg.index, quarterly_avg.values, marker='o', color='#2ECC71', label='분기별 평균 상대습도')
plt.title('한국 분기별 평균 상대습도', fontsize=16)
plt.xlabel('분기', fontsize=12)
plt.ylabel('상대습도 (%)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.xticks(range(len(x_ticks)), x_labels, rotation=45)  # 커스텀 x축 레이블 설정
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

# 5. 지역별 연간 평균 상대습도 시각화
regions = ["강릉", "대구", "대전", "부산", "서울", "수원", "영광군", "원주", "창원", "춘천", "포항", "홍천"]

for region in regions:
    regional_annual_avg = weather_data[weather_data['지역'] == region].groupby('연도')['일 평균 상대습도 (%)'].mean().round(1)

    plt.figure(figsize=(12, 6))
    plt.plot(regional_annual_avg.index, regional_annual_avg.values, marker='o', label=f'{region} 연간 평균 상대습도', color='#FF5733')
    plt.title(f'{region} 연간 평균 상대습도', fontsize=16)
    plt.xlabel('연도', fontsize=12)
    plt.ylabel('상대습도 (%)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()

# 6. 지역별 분기별 평균 상대습도 시각화
for region in regions:
    regional_quarterly_avg = weather_data[weather_data['지역'] == region].groupby('연도_분기')['일 평균 상대습도 (%)'].mean().round(1)
    
    # x축 레이블 커스텀: 각 해의 1분기만 표시
    x_ticks = regional_quarterly_avg.index
    x_labels = [tick if '1분기' in tick else '' for tick in x_ticks]
    
    plt.figure(figsize=(12, 6))
    plt.plot(regional_quarterly_avg.index, regional_quarterly_avg.values, marker='o', label=f'{region} 분기별 평균 상대습도', color='#2ECC71')
    plt.title(f'{region} 분기별 평균 상대습도', fontsize=16)
    plt.xlabel('분기', fontsize=12)
    plt.ylabel('상대습도 (%)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(range(len(x_ticks)), x_labels, rotation=45)  # 커스텀 x축 레이블 설정
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()
