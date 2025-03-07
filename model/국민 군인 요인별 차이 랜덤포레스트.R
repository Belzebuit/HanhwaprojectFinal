library(tidyverse)
library(lubridate)
library(readxl)
data <- read_excel("./Processed_COVID_Data_Filled_종합.xlsx")
View(data)
data$'국민감염자수' <- as.numeric(data$'국민감염자수')
data$'군인감염자수' <- as.numeric(data$'군인감염자수')
str(data)
summary(data)
data$Date <- as.Date(data$Date,format='%Y-%m-%d')
data$year <- year(data$Date)
military_population <- 500000           # 군인 수: 50만 명
public_population_2020 <- 51830000      # 2020년 국민 수
public_population_2021 <- 51640000      # 2021년 국민 수
data$public_population <- ifelse(data$year == 2020, 
                                 public_population_2020, 
                                 ifelse(data$year == 2021, public_population_2021, NA))
data$military_infection_rate <- data$군인감염자수 / military_population
data$public_infection_rate   <- data$국민감염자수 / data$public_population

names(data)
sum(is.na(data))

# 국민 대상 다중회귀분석
model_public <- lm(public_infection_rate ~ SO2 + CO + O3 + NO2 + PM10 + PM25 +
                     `평균기온(℃)` + `평균최고기온(℃)` + `최고기온(℃)` +
                     `평균최저기온(℃)` + `최저기온(℃)` +
                     `평균일강수량(mm)` + `최다일강수량(mm)` +
                     `평균풍속(m/s)` + `최대풍속(m/s)` + `최대순간풍속(m/s)` +
                     `평균습도(%rh)` + `최저습도(%rh)` +
                     `일조합(hr)` + `일사합(MJ/m2)`+`대중교통이용량`,
                   data = data)
summary(model_public)  # 국민 모델 결과

# 군인 대상 다중회귀분석
model_military <- lm(military_infection_rate ~ SO2 + CO + O3 + NO2 + PM10 + PM25 +
                       `평균기온(℃)` + `평균최고기온(℃)` + `최고기온(℃)` +
                       `평균최저기온(℃)` + `최저기온(℃)` +
                       `평균일강수량(mm)` + `최다일강수량(mm)` +
                       `평균풍속(m/s)` + `최대풍속(m/s)` + `최대순간풍속(m/s)` +
                       `평균습도(%rh)` + `최저습도(%rh)` +
                       `일조합(hr)` + `일사합(MJ/m2)` + `대중교통이용량`,
                     data = data)
summary(model_military)  # 군인 모델 결과

library(randomForest)

# 변수명을 영어로 변경
colnames(data) <- make.names(colnames(data))

# 랜덤 포레스트 실행
rf_model <- randomForest(public_infection_rate ~ ., data = data, importance = TRUE)
print(rf_model)

# 변수 중요도 확인
importance(rf_model)
varImpPlot(rf_model)

# 훈련 데이터(70%)와 테스트 데이터(30%) 나누기
set.seed(123)
train_idx <- sample(1:nrow(data), 0.7 * nrow(data))
train_data <- data[train_idx, ]
test_data <- data[-train_idx, ]

# Random Forest 모델 다시 학습
rf_model <- randomForest(public_infection_rate ~ ., data = train_data, importance = TRUE)

# 테스트 데이터 예측
y_pred_rf <- predict(rf_model, newdata = test_data)

# 테스트 데이터에서 MSE & R² 계산
mse_rf <- mean((test_data$public_infection_rate - y_pred_rf)^2)
sst_rf <- sum((test_data$public_infection_rate - mean(test_data$public_infection_rate))^2)
sse_rf <- sum((test_data$public_infection_rate - y_pred_rf)^2)
r_squared_rf <- 1 - (sse_rf / sst_rf)

print(paste("Test MSE (Random Forest):", mse_rf))
print(paste("Test R-squared (Random Forest):", r_squared_rf))

# 변수 중요도 출력
print(importance(rf_model))

# 변수 중요도 시각화
print(varImpPlot(rf_model))

library(ggplot2)

p <- ggplot(data, aes(x = Date, y = 국민감염자수)) +
  geom_line(color = "blue") +
  labs(title = "국민 감염자수 추이", x = "날짜", y = "국민 감염자수") +
  theme_minimal()

print(p)  # 명시적으로 그래프 출력

p2 <- ggplot(data, aes(x = 평균기온..., y = public_infection_rate)) +
  geom_point(alpha = 0.5, color = "red") +
  geom_smooth(method = "lm", col = "blue") +
  labs(title = "평균기온과 감염률의 관계", x = "평균기온 (℃)", y = "감염률") +
  theme_minimal()

print(p2)  # 그래프 출력

p3 <- ggplot(data, aes(x = 대중교통이용량, y = public_infection_rate)) +
  geom_point(alpha = 0.5, color = "darkgreen") +
  geom_smooth(method = "lm", col = "red") +
  labs(title = "대중교통 이용량과 감염률의 관계", x = "대중교통 이용량", y = "감염률") +
  theme_minimal()

print(p3)  # 그래프 출력

# 계절 변수 추가
data$season <- ifelse(format(data$Date, "%m") %in% c("12", "01", "02"), "Winter",
                      ifelse(format(data$Date, "%m") %in% c("03", "04", "05"), "Spring",
                             ifelse(format(data$Date, "%m") %in% c("06", "07", "08"), "Summer", "Fall")))

# 계절별 감염률 비교
p4 <- ggplot(data, aes(x = season, y = public_infection_rate)) +
  geom_boxplot(fill = "lightblue") +
  labs(title = "계절별 감염률 비교", x = "계절", y = "감염률") +
  theme_minimal()

print(p4)  # 그래프 출력



