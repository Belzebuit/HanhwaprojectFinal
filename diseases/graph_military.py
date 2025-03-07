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

# Load the data from CSV
file_path = './기본통계_군_질병별_분류.csv'  # Set default file path
data = pd.read_csv(file_path, encoding='cp949')

# Calculate the percentage of each classification per year
classification_summary = data.groupby(['연도', '질병분류'])['현황'].sum().reset_index()
total_per_year = data.groupby(['연도'])['현황'].sum().reset_index().rename(columns={'현황': '총합'})
classification_percentage = classification_summary.merge(total_per_year, on='연도')
classification_percentage['퍼센트'] = (classification_percentage['현황'] / classification_percentage['총합']) * 100

# Pivot the data for easier plotting
pivot_data = classification_percentage.pivot(index='연도', columns='질병분류', values='퍼센트').fillna(0)

# Plot the data with percentage values and Korean font
plt.figure(figsize=(12, 6))
bar_plot = pivot_data.plot(kind='bar', stacked=True, figsize=(12, 6), legend=False)

# Add labels on each bar
for container in bar_plot.containers:
    bar_plot.bar_label(container, fmt='%.1f%%', label_type='center', fontsize=8, color='white')

# Configure font and layout
plt.title('질병분류별 연도별 퍼센테이지 분포(군)', fontsize=16)
plt.ylabel('퍼센테이지 (%)', fontsize=12)
plt.xlabel('연도', fontsize=12)
plt.legend(title='질병분류', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()