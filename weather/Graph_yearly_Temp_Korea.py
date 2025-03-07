import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 한글 폰트 경로 설정 (환경에 맞게 수정)
font_path = 'C:/Windows/Fonts/malgun.ttf'  # Windows 예제
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

# 데이터 불러오기
file_path = './yearly_averages_korea.csv'  # 실제 파일 경로
data = pd.read_csv(file_path, encoding='cp949')

# 연도별 최고기온, 최저기온, 평균기온 변화 시각화
plt.figure(figsize=(12, 6))
plt.plot(data['연도'], data['최고기온 (C)'], label='최고기온 (℃)', marker='o', color='#FF5733')  # 오렌지색
plt.plot(data['연도'], data['최저기온 (C)'], label='최저기온 (℃)', marker='o', color='#3498DB')  # 하늘색
plt.plot(data['연도'], data['일 평균기온 (C)'], label='일 평균기온 (℃)', marker='o', color='#2ECC71')  # 라임 그린

# x축 단위를 1년 단위로 설정
plt.xticks(data['연도'], rotation=45)

# 그래프 꾸미기
plt.title('연도별 최고/최저/평균기온 변화', fontsize=16)
plt.xlabel('연도', fontsize=12)
plt.ylabel('기온 (°C)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12)
plt.tight_layout()

# 범례를 그래프 외부로 이동
plt.legend(fontsize=12, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)


# 그래프 출력
plt.show()
