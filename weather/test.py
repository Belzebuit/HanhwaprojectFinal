import pandas as pd

# 파일 경로
file_path = './1224weather.csv'

# ANSI 인코딩으로 파일 읽기
try:
    df = pd.read_csv(file_path, encoding='cp949')  # 한국어 ANSI
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding='cp1252')  # 서유럽 ANSI

# 빈 행 제거
df_cleaned = df.dropna(how='all')  # NaN 값만 있는 행 제거
df_cleaned = df_cleaned.loc[~(df_cleaned == "").all(axis=1)]  # 빈 문자열만 있는 행 제거

# 결과 저장
output_path = "cleaned_1224weather.csv"
df_cleaned.to_csv(output_path, index=False, encoding='cp949')  # 저장 시에도 인코딩 유지

print(f"빈 행 제거 완료! 결과는 {output_path}에 저장되었습니다.")
