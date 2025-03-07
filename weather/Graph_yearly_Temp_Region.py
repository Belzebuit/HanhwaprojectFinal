import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 한글 폰트 설정 (환경에 맞게 수정)
font_path = 'C:/Windows/Fonts/malgun.ttf'  # Windows 예제
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

# 데이터 불러오기
file_path = './yearly_averages_by_region.csv'  # 실제 파일 경로
regional_data = pd.read_csv(file_path, encoding='cp949')

# 시각화 대상 지역
target_regions = ["강릉", "대구", "대전", "부산", "서울", "수원",
                  "영광군", "원주", "창원", "춘천", "포항", "홍천","청주"]

# 각 지역별 그래프 생성
for region in target_regions:
    region_data = regional_data[regional_data['지역'] == region]
    
    # 그래프 생성
    plt.figure(figsize=(10, 6))
    plt.plot(region_data['연도'], region_data['최고기온 (C)'], label='최고기온 (℃)', marker='o', color='#FF5733')  # 오렌지색
    plt.plot(region_data['연도'], region_data['최저기온 (C)'], label='최저기온 (℃)', marker='o', color='#3498DB')  # 하늘색
    plt.plot(region_data['연도'], region_data['일 평균기온 (C)'], label='일 평균기온 (℃)', marker='o', color='#2ECC71')  # 라임 그린

    # 그래프 꾸미기
    plt.title(f'{region} 연도별 기온 변화', fontsize=16)
    plt.xlabel('연도', fontsize=12)
    plt.ylabel('기온 (°C)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)

    # 범례를 그래프 외부로 이동
    plt.legend(fontsize=12, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

    # 그래프의 여백 조정 (범례가 잘리지 않도록)
    plt.tight_layout(rect=[0, 0.1, 1, 1])  # 아래 여백 추가

    # 그래프 출력
    plt.show()
