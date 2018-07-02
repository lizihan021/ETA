import pickle

with open("weather_data.txt", "rb") as fp:
    month_data = pickle.load(fp)


day = 1 # Nov 1
hour = 20 # 20:00
data_type = 2 # 1 ~ weather condition, 2 ~ visibility

print month_data[day + 1][hour][data_type]