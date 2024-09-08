from time import sleep
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import uuid
import json
import re
import os
from random import randint
from pprint import pprint


result_dir: str = "./result"
if not os.path.isdir(result_dir):
	os.mkdir(result_dir)

request_headers = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}
requested_url: str = "https://www.gutenberg.org/browse/languages/zh"
base_url: str = "https://www.gutenberg.org"

response = requests.get(requested_url, headers=request_headers)
page = BeautifulSoup(response.text, "lxml")

book_list = page.select_one("div.pgdbbylanguage").select("li > a")
for book in book_list[:200]:
	response = requests.get(f"{base_url}{book.get('href')}", headers=request_headers)
	book_page = BeautifulSoup(response.text, "lxml")

	book_info: dict = {}
	needy_data: list = ["Author", "Title", "Release Date"]
	for data in book_page.select_one("div.page-body").select("table.bibrec")[0].select("tr")[:-1]:
		key: str = data.find("th").get_text().strip()
		if key not in needy_data:
			continue
		book_info[key.lower().replace(" ", "_")] = data.find("td").get_text().strip()

	try:
		book_info["release_date"] = str(datetime.strptime(book_info["release_date"], "%B %d, %Y").date())
	except ValueError:
		book_info["release_date"] = str(datetime.strptime(book_info["release_date"], "%b %d, %Y").date())

	for file in book_page.select_one("div.page-body").select("table.files")[0].select("a.link"):
		if file.get_text() == "Plain Text UTF-8":
			response = requests.get(f"{base_url}{file.get('href')}", headers=request_headers)
			content_page = BeautifulSoup(response.text, "lxml")
			book_info["content"] = content_page.select_one("body > p").get_text().split("***")[2].strip()
			break
	pprint(book_info)
	with open(f"{result_dir}/{book_info['title'].replace(' ', '_').replace('/', '_')}.json", "w", encoding="utf-8") as file:
		file.write(json.dumps(book_info, indent=4))
