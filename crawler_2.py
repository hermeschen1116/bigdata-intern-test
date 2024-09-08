from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import uuid
import json
import re
import os
from random import randint


result_dir: str = "./result"
if not os.path.isdir(result_dir):
	os.mkdir(result_dir)

request_headers = {
	"cookie": "over18=1",
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}
requested_url: str = "https://www.ptt.cc/bbs/Gossiping/index.html"
base_url: str = "https://www.ptt.cc"

today_date = datetime.today().date()
end_date = (datetime.today() - timedelta(days=7)).date()

reach_end_date: bool = False
while not reach_end_date:
	try:
		response = requests.get(requested_url, headers=request_headers, timeout=0.5)
	except requests.ReadTimeout:
		continue
	page = BeautifulSoup(response.text, "lxml")

	for article in page.select("div.r-ent"):
		article_data: dict = {}
		article_url: str = article.select_one("div.title > a")
		if article_url is None:
			continue	# skip deleted article

		article_data["title"] = article_url.get_text()
		article_genre = re.findall("\\[.*\\]", article_data["title"])
		article_data["genre"] = " " if len(article_genre) == 0 else article_genre[0]
		article_data["author"] = article.select_one("div.author").get_text()

		article_response = requests.get(f"{base_url}{article_url.get('href')}", headers=request_headers)
		article_page = BeautifulSoup(article_response.text, "lxml")

		article_header = article_page.select("span.article-meta-value")
		if len(article_header) != 0:	# deal with article without header
			article_publish_time = article_header[-1].get_text()
			article_publish_time = datetime.strptime(article_publish_time, "%a %b %d %H:%M:%S %Y")
			if article_publish_time.date() == end_date:
				reach_end_date = True
				break	# end for article out of time range
			if (article_publish_time.date() <= end_date) or (article_publish_time.date() > today_date):
				break	# skip for article out of time range
			article_data["publish_time"] = str(article_publish_time)
		else:
			article_data["publish_time"] = ""
		article_data["content"] = "\n".join(article_page.find(id="main-content").get_text().split("--")[0].strip().splitlines()[1:])

		article_data["comments"] = []
		article_comments: list = article_page.select("div.push")
		for comment in article_comments:
			comment_data: dict = {}
			try:
				comment_data["user"] = comment.find("span", class_="push-userid").get_text()
			except AttributeError:
				continue
			comment_data["content"] = comment.find("span", class_="push-content").get_text()
			comment_publish_time_without_year: str = " ".join(comment.find("span", class_="push-ipdatetime").get_text().strip().split(" ")[1:])
			try:
				commet_publish_time: datetime = datetime.strptime(f"{today_date.year}/{comment_publish_time_without_year}", "%Y/%m/%d %H:%M")
				if (len(article_data["comments"]) != 0) and \
					(datetime.strptime(article_data["comments"][-1]["publish_time"], "%Y-%m-%d %H:%M:%S") > commet_publish_time):
					commet_publish_time = datetime.strptime(f"{today_date.year + 1}/{comment_publish_time_without_year}", "%Y/%m/%d %H:%M")
				comment_data["publish_time"] = str(commet_publish_time)
			except ValueError:
				continue

			article_data["comments"].append(comment_data)
		with open(f"{result_dir}/article-{uuid.uuid4()}.json", "w", encoding="utf-8") as file:
			file.write(json.dumps(article_data, indent=4))

	requested_url = base_url + page.select_one("#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)").get("href")
