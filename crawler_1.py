from bs4 import BeautifulSoup
import requests
import json

request_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
requested_url: str = "https://www.ptt.cc/bbs/index.html"

response = requests.get(requested_url, headers=request_headers)

page = BeautifulSoup(response.text, "html.parser")
top_board = page.find("div", class_="b-ent")
top_board_name: str = top_board.find("div", class_="board-name").text
base_url: str = "https://www.ptt.cc"
top_board_url: str = base_url + top_board.find("a", class_="board").get("href")

result: dict = {"board_name": top_board_name, "board_url": top_board_url}
with open("result.json", "w", encoding="utf-8") as file:
	file.write(json.dumps(result, indent="4"))
