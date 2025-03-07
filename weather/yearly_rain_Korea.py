import pandas as pd

# Load the weather data
file_path_weather = './12-24weather.csv'
weather_data = pd.read_csv(file_path_weather, encoding='EUC-KR')

# Convert '관측시각 (KST)' to datetime for easier processing
weather_data['관측시각 (KST)'] = pd.to_datetime(weather_data['관측시각 (KST)'], format='%Y%m%d', errors='coerce')

# Add columns for year and quarter
weather_data['Year'] = weather_data['관측시각 (KST)'].dt.year
weather_data['Quarter'] = weather_data['관측시각 (KST)'].dt.quarter

# Handle missing or problematic data in '일강수량 (mm)'
weather_data['일강수량 (mm)'] = pd.to_numeric(weather_data['일강수량 (mm)'], errors='coerce').fillna(0)

# Calculate the required metrics
annual_rainfall = weather_data.groupby('Year')['일강수량 (mm)'].mean().reset_index(name='연간 평균 강수량 (mm)')
quarterly_rainfall = weather_data.groupby(['Year', 'Quarter'])['일강수량 (mm)'].mean().reset_index(name='분기별 평균 강수량 (mm)')
region_annual_rainfall = weather_data.groupby(['Year', '지역'])['일강수량 (mm)'].mean().reset_index(name='지역별 연간 평균 강수량 (mm)')
region_quarterly_rainfall = weather_data.groupby(['Year', 'Quarter', '지역'])['일강수량 (mm)'].mean().reset_index(name='지역별 분기별 평균 강수량 (mm)')

# Round values to 2 decimal places
annual_rainfall['연간 평균 강수량 (mm)'] = annual_rainfall['연간 평균 강수량 (mm)'].round(2)
quarterly_rainfall['분기별 평균 강수량 (mm)'] = quarterly_rainfall['분기별 평균 강수량 (mm)'].round(2)
region_annual_rainfall['지역별 연간 평균 강수량 (mm)'] = region_annual_rainfall['지역별 연간 평균 강수량 (mm)'].round(2)
region_quarterly_rainfall['지역별 분기별 평균 강수량 (mm)'] = region_quarterly_rainfall['지역별 분기별 평균 강수량 (mm)'].round(2)

# Save the results to CSV files with ANSI encoding
output_paths = {
    "Korea_yearly_rainfall.csv": annual_rainfall,
    "Korea_quarterly_rainfall.csv": quarterly_rainfall,
    "region_yearly_rainfall.csv": region_annual_rainfall,
    "region_quarterly_rainfall.csv": region_quarterly_rainfall
}

for file_name, df in output_paths.items():
    output_path = f"./{file_name}"
    df.to_csv(output_path, index=False, encoding='ansi')
