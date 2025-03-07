import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import platform

# Set Korean font for matplotlib depending on the OS
if platform.system() == 'Windows':
    rc('font', family='Malgun Gothic')  # For Windows
elif platform.system() == 'Darwin':
    rc('font', family='AppleGothic')  # For macOS
else:
    rc('font', family='NanumGothic')  # For Linux (requires NanumGothic installed)

# Ensure minus sign is shown correctly
plt.rcParams['axes.unicode_minus'] = False

# Load the data
file_path = '5종특정_질병별_분류(2012-2024).csv'
data = pd.read_csv(file_path, encoding='cp949')

# Drop unnecessary columns
data = data.drop(columns=[col for col in data.columns if "Unnamed" in col])

# Convert '현황' to numeric and handle non-numeric values
data['현황'] = pd.to_numeric(data['현황'], errors='coerce')

# Drop rows with NaN values in critical columns
data = data.dropna(subset=['연도', '현황', '질병분류'])

# Ensure '연도' is an integer
data['연도'] = data['연도'].astype(int)

# Filter data from 2015 to 2021
data = data[(data['연도'] >= 2015) & (data['연도'] <= 2021)]

# Calculate the percentage of each classification per year
classification_summary = data.groupby(['연도', '질병분류'])['현황'].sum().reset_index()
total_per_year = data.groupby(['연도'])['현황'].sum().reset_index().rename(columns={'현황': '총합'})
classification_percentage = classification_summary.merge(total_per_year, on='연도')
classification_percentage['퍼센트'] = (classification_percentage['현황'] / classification_percentage['총합']) * 100

# Pivot the data for easier plotting
pivot_data = classification_percentage.pivot(index='연도', columns='질병분류', values='퍼센트').fillna(0)

# Define custom colors for each disease category
custom_colors = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

# Plot the data with percentage values and Korean font
plt.figure(figsize=(12, 6))
bar_plot = pivot_data.plot(
    kind='bar', 
    stacked=True, 
    figsize=(12, 6), 
    color=custom_colors[:len(pivot_data.columns)], 
    legend=False
)

# Add labels on each bar
for container in bar_plot.containers:
    bar_plot.bar_label(container, fmt='%.1f%%', label_type='center', fontsize=8, color='white')

# Configure font and layout
plt.title('질병분류별 연도별 퍼센테이지 분포 (한국)', fontsize=16)
plt.ylabel('퍼센테이지 (%)', fontsize=12)
plt.xlabel('연도', fontsize=12)
plt.legend(title='질병분류', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
