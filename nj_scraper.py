import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import random
import pandas as pd
import os
from subprocess import call

def scrape_event_page(driver, dr):
	try:
		file_name = dr["link"].split("/")[-1]
		output_txt = "output.txt"
		driver.get(dr["link"])
		
		# ocrmypdf --sidecar output.txt ~/Desktop/20161007_25MA04585100.pdf output.pdf
		# run osrmypdf on that local pdf
		call(["ocrmypdf", "--sidecar", output_txt, file_name, "/dev/null"])

		with open(output_txt) as f: 
			data = f.read()
		dr['data'] = data
		os.remove(file_name)
		print(dr)
	except Exception as error:
		print(dr["name"] + " exception")
		dr['data'] = pd.NA
		print(error)

def scrape_all_actions(driver):
	driver.get("https://www.njconsumeraffairs.gov/bme/Pages/actions.aspx")

	scroll_count = 1
	for _ in range(scroll_count):
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		wait_time = 2 * random.randint(2,4)
		time.sleep(wait_time)  # Wait for the new results to load                  

	page_source = driver.page_source
	soup = BeautifulSoup(page_source, 'html.parser')
	search_results = soup.find_all('tr')
	event_list = []
	for i in range(len(search_results)-1):
		try:
			obj = {}
			entries = search_results[i+1].find_all('td')
			obj['name'] = entries[0].get_text()
			obj['license_num'] = entries[1].get_text()
			a_val = entries[2].find('a')
			obj['link'] = a_val['href']
			obj['order'] = a_val.get_text()
			obj['date'] = entries[3].get_text()
			event_list.append(obj)
		except:
			print("error with entry")
	return event_list

def uploadFile(df):
	df.to_csv("s3://drmal123/nj3.csv", index=False)

if __name__ == "__main__":
	options = webdriver.ChromeOptions()
	options.add_experimental_option('prefs', {
		"download.default_directory": "/Users/Plato/Desktop/dr", #Change default directory for downloads
		"download.prompt_for_download": False, #To auto download the file
		"download.directory_upgrade": True,
		"plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
	})
	driver = webdriver.Chrome(options=options)
	dr_list = scrape_all_actions(driver)
	index = 0
	for dr in dr_list:
		index += 1
		print(str(index) + " doctor")
		scrape_event_page(driver, dr)
	df = pd.DataFrame(columns=["Name", "License Num", "Order","Date", "Link", "Data"])
	for dr in dr_list:
		df = pd.concat(
					[pd.DataFrame([[dr['name'], dr['license_num'], dr['order'], dr['date'], dr['link'], dr['data']]], columns=df.columns), df],
		ignore_index=True,)
	uploadFile(df)
	print("Success")
