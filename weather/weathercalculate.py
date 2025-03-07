import pandas as pd

# CSV 파일 읽기
file_path = './2024weather.csv'  # 파일 경로 설정
data = pd.read_csv(file_path)

# 관측시각을 datetime 형식으로 변환
data['관측시각 (KST)'] = pd.to_datetime(data['관측시각 (KST)'], format='%Y%m%d')
data['연도'] = data['관측시각 (KST)'].dt.year
data['월'] = data['관측시각 (KST)'].dt.month
data['분기'] = data['관측시각 (KST)'].dt.to_period('Q')

# 월별 평균 계산
def calculate_monthly_means(df):
    return df.groupby('월').agg({
        '일 평균기온 (C)': 'mean',
        '일교차 (C)': 'mean',
        '최고기온 (C)': 'mean',
        '최저기온 (C)': 'mean',
        '일 평균 상대습도 (%)': 'mean'
    }).rename(columns={
        '일 평균기온 (C)': '월평균기온',
        '일교차 (C)': '월평균일교차',
        '최고기온 (C)': '월평균최고기온',
        '최저기온 (C)': '월평균최저기온',
        '일 평균 상대습도 (%)': '월평균상대습도'
    }).round(2)

# 분기별 평균 계산
def calculate_quarterly_means(df):
    return df.groupby('분기').agg({
        '일 평균기온 (C)': 'mean',
        '일교차 (C)': 'mean',
        '최고기온 (C)': 'mean',
        '최저기온 (C)': 'mean',
        '일 평균 상대습도 (%)': 'mean'
    }).rename(columns={
        '일 평균기온 (C)': '분기평균기온',
        '일교차 (C)': '분기평균일교차',
        '최고기온 (C)': '분기평균최고기온',
        '최저기온 (C)': '분기평균최저기온',
        '일 평균 상대습도 (%)': '분기평균상대습도'
    }).round(2)

# 전체 데이터에 대한 평균 계산
overall_monthly_means = calculate_monthly_means(data).reset_index()
overall_monthly_means['구분'] = '월별'
overall_quarterly_means = calculate_quarterly_means(data).reset_index()
overall_quarterly_means['구분'] = '분기별'

overall_combined = pd.concat([overall_monthly_means, overall_quarterly_means], ignore_index=True)
overall_combined.to_csv('./2024_Korea_summary.csv', encoding='utf-8-sig', index=False)

# 지점번호별 평균 계산
def calculate_station_means(group):
    monthly = calculate_monthly_means(group).reset_index()
    monthly['구분'] = '월별'
    quarterly = calculate_quarterly_means(group).reset_index()
    quarterly['구분'] = '분기별'
    return pd.concat([monthly, quarterly], ignore_index=True)

station_data = []
for station, group in data.groupby('국내 지점번호'):
    station_df = calculate_station_means(group)
    station_df['지점번호'] = station
    station_data.append(station_df)

station_combined = pd.concat(station_data, ignore_index=True)
station_combined.to_csv('./2024_station_summary.csv', encoding='utf-8-sig', index=False)

print("한국 전체 및 지역별 월별, 분기별 평균 계산 완료 및 저장됨.")