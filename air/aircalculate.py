import pandas as pd

# Load the CSV file
data_csv = pd.read_csv('./1224air.csv')

# Target cities for analysis
target_cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "수원", "강릉"]

# Data preprocessing
data_csv["관측시간"] = data_csv["관측시간"].astype(str).str.strip()
data_csv = data_csv[data_csv["관측시간"].str.isnumeric()]
data_csv["관측시간"] = data_csv["관측시간"].astype(int)

data_csv["Year"] = data_csv["관측시간"].astype(str).str[:4].astype(int)
data_csv["Month"] = data_csv["관측시간"].astype(str).str[4:6].astype(int)
data_csv["Quarter"] = (data_csv["Month"] - 1) // 3 + 1

# Filter for target cities
filtered_data = data_csv[data_csv["지역"].isin(target_cities)]

# Columns to calculate averages
pollutants = ["PM2.5(μg/m³)", "PM10(μg/m³)", "아황산가스(ppm)", "오존(ppm)", "이산화질소(ppm)", "일산화질소(ppm)"]

# Ensure pollutant columns are numeric
for col in pollutants:
    filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

# Filter PM2.5 data from 2015 onwards
filtered_data_pm25 = filtered_data[(filtered_data["Year"] >= 2015) & (filtered_data["PM2.5(μg/m³)"].notna())]

# Calculate yearly averages
yearly_avg = filtered_data.groupby(["지역", "Year"])[pollutants].mean().reset_index()

# Round specific pollutants to different decimal places
yearly_avg["PM2.5(μg/m³)"] = yearly_avg["PM2.5(μg/m³)"].round(1)
yearly_avg["PM10(μg/m³)"] = yearly_avg["PM10(μg/m³)"].round(1)
yearly_avg["아황산가스(ppm)"] = yearly_avg["아황산가스(ppm)"].round(4)
yearly_avg["오존(ppm)"] = yearly_avg["오존(ppm)"].round(4)
yearly_avg["이산화질소(ppm)"] = yearly_avg["이산화질소(ppm)"].round(4)
yearly_avg["일산화질소(ppm)"] = yearly_avg["일산화질소(ppm)"].round(4)

# Calculate quarterly averages
quarterly_avg = filtered_data.groupby(["지역", "Year", "Quarter"])[pollutants].mean().reset_index()

# Round specific pollutants to different decimal places
quarterly_avg["PM2.5(μg/m³)"] = quarterly_avg["PM2.5(μg/m³)"].round(1)
quarterly_avg["PM10(μg/m³)"] = quarterly_avg["PM10(μg/m³)"].round(1)
quarterly_avg["아황산가스(ppm)"] = quarterly_avg["아황산가스(ppm)"].round(4)
quarterly_avg["오존(ppm)"] = quarterly_avg["오존(ppm)"].round(4)
quarterly_avg["이산화질소(ppm)"] = quarterly_avg["이산화질소(ppm)"].round(4)
quarterly_avg["일산화질소(ppm)"] = quarterly_avg["일산화질소(ppm)"].round(4)

# Save results to CSV files
yearly_avg.to_csv('region_yearly_avg.csv', index=False, encoding="utf-8-sig")
quarterly_avg.to_csv('region_quarterly_avg.csv', index=False, encoding="utf-8-sig")

print("Yearly and quarterly averages saved as 'region_yearly_avg.csv' and 'region_quarterly_avg.csv'.")
