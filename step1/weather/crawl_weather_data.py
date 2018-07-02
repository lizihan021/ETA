from pyvirtualdisplay import Display
from selenium import webdriver
import pickle

display = Display(visible=0, size=(800, 600))
display.start()
driver = webdriver.Chrome()
driver.get('https://www.timeanddate.com/weather/china/chengdu/historic?month=11&year=2016')

month_data = []
for idx in range(1, 31):
    day_data = []
    driver.find_element_by_link_text("Nov "+str(idx)).click()
    table = driver.find_element_by_id("wt-his")
    for row in table.find_elements_by_tag_name("tr"):
        row_header = row.find_elements_by_tag_name("th")
        cells = row.find_elements_by_tag_name("td")
        if len(cells) > 1:
            hour_data = [row_header[0].text, cells[2].text, cells[7].text]
            print hour_data
            day_data.append(hour_data)
    month_data.append(day_data)


# print driver.title
# print month_data
# print "-----------------------------------"

with open("weather_data.txt", "wb") as fp:
    pickle.dump(month_data, fp)

with open("weather_data.txt", "rb") as fp:
    test_data = pickle.load(fp)

# print test_data