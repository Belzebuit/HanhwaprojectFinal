import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# 🔹 1. 엑셀 데이터 불러오기
file_path = "Processed_COVID_Data_Filled_종합.xlsx"
xls = pd.ExcelFile(file_path)
df = pd.read_excel(xls, sheet_name="Processed_COVID_Data_Filled_종합")

# 🔹 2. 날짜 순 정렬
df = df.sort_values(by="Date")

# 🔹 3. 이동 평균 추가 (최근 7일 감염자 수 평균 추가)
df["군인감염자수_7일이동평균"] = df["군인감염자수"].rolling(window=7).mean().fillna(0)

# 🔹 4. 날짜(`Date`) 컬럼 제외 후 features 리스트 생성
features = [col for col in df.columns if col != "Date"]  # 'Date' 컬럼 제외

# 🔹 5. 데이터 정규화 (StandardScaler 사용)
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[features] = scaler.fit_transform(df[features])  # 정규화 적용

# 🔹 6. 시퀀스 데이터 생성 (30일 입력)
def create_sequences(data, target_col, seq_length=60):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, target_col])
    return np.array(X), np.array(y)

# 🔹 7. 입력 데이터 배열 생성 (25개 변수 사용)
data_values = df_scaled[features].values  # features 리스트 반영
target_col_index = features.index("군인감염자수")  # '군인감염자수' 위치 찾기

X, y = create_sequences(data_values, target_col_index, seq_length=60)

# 🔹 8. 훈련/검증 데이터 분할
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

# 🔹 9. 데이터 크기 확인 (입력 차원이 맞는지 체크)
print(f"features 개수: {len(features)}")  # 25개인지 확인
print(f"df_scaled의 shape: {df_scaled.shape}")  # (700, 25) 확인
print(f"X_train shape: {X_train.shape}")  # (샘플 수, 30, 25) 확인

# 🔹 10. LSTM 모델 정의
model = Sequential([
    LSTM(256, activation='tanh', return_sequences=True, input_shape=(30, X_train.shape[-1])),
    Dropout(0.3),
    LSTM(128, activation='tanh', return_sequences=True),
    Dropout(0.3),
    LSTM(64, activation='tanh', return_sequences=False),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dense(1)
])

# 🔹 11. 모델 컴파일
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Early Stopping 설정 (검증 손실이 5 에포크 이상 개선되지 않으면 학습 중단)
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# 🔹 12. 모델 학습
history = model.fit(X_train, y_train, epochs=100, batch_size=32,
                    validation_data=(X_val, y_val), callbacks=[early_stopping])

# 🔹 13. 예측 수행
y_pred = model.predict(X_val)

# 🔹 14. MAE 및 RMSE 계산 및 출력
mae_value = mean_absolute_error(y_val, y_pred)
rmse_value = np.sqrt(mean_squared_error(y_val, y_pred))

print(f"🔹 MAE (Mean Absolute Error): {mae_value:.4f}")
print(f"RMSE (Root Mean Squared Error): {rmse_value:.4f}")

# 🔹 15. 예측 결과 시각화
plt.figure(figsize=(10, 5))
plt.plot(y_val, label="Actual infection", color='blue')
plt.plot(y_pred, label="Predicted infection", color='red', linestyle='dashed')
plt.legend()
plt.title(f"LSTM Military Infection Predict (MAE: {mae_value:.4f})")
plt.xlabel("Time")
plt.ylabel("Scaled Military Infector")
plt.show()
