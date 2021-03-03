# !pip install selenium
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib
import csv

games_url = []

for page in range(1, 3) :
    url = f"https://boardlife.co.kr/game_rank.php?tb=&pg={page}&file=&file2=&view_id="
    base_url = "https://boardlife.co.kr/"

    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    
    table = soup.select("table.new_game")
    for item in table :
        games_url.append({
            "ranking" : int(item.select_one("td.ranking").get_text()),
            "title" : item.select_one("a.game_title").get_text().strip(),
            "url" : item.select_one("a.game_title")['href']
        })


options = webdriver.ChromeOptions()
options.add_argument('headless') # 웹 브라우저를 띄우지 않는 headless chrome 옵션 적용
options.add_argument('disable-gpu') # GPU 사용 안함
options.add_argument('lang=ko_KR') # 언어 설정

chromedriver = './chromedriver.exe'
driver = webdriver.Chrome(chromedriver, options=options)

games = []
for game in games_url :
    print(f"{game['ranking']} : {game['title']}")
    game_url = base_url + game['url']
    driver.get(url=game_url)

    # 발매연도
    year = driver.find_element_by_xpath('/html/body/div[3]/table//tr/td/table//tr/td/table[1]//tr[3]/td[1]/div[1]/div[2]/div/table//tr/td[3]/table//tr[3]/td/table//tr/td[2]/table//tr[1]/td')
    year = year.text.split('(')[-1]
    year = int(year[:-2])
    print(year)

    # 영어 이름
    title_eng = driver.find_element_by_xpath('/html/body/div[3]/table//tr/td/table//tr/td/table[1]//tr[3]/td[1]/div[1]/div[2]/div/table//tr/td[3]/table//tr[3]/td/table//tr/td[2]/table//tr[2]/td')
    title_eng = title_eng.text.lower().replace(" ", "_")

    # 이미지 저장
    img_data = driver.find_element_by_xpath('/html/body/div[3]/table//tr/td/table//tr/td/table[1]//tr[3]/td[1]/div[1]/div[2]/div/table//tr/td[1]/table//tr[1]/td/img')
    with urllib.request.urlopen(img_data.get_attribute('src')) as f :
        with open(f'./image/{title_eng}.png', 'wb') as h :
            img = f.read()
            h.write(img)

    # 게임인원, 플레이 시간, 사용연령, 게임난이도
    details = driver.find_elements_by_xpath('/html/body/div[3]/table//tr/td/table//tr/td/table[1]//tr[3]/td[1]/div[1]/div[2]/div/table//tr/td[3]/table//tr[5]/td/table//tr/td')
    for detail in details :
        data_title = detail.find_element_by_tag_name('span').text
        data = detail.find_element_by_tag_name('p').text

        if data_title == "게임인원" :
            data = data.replace("명", "").split("-")
            people_min = int(data[0])
            people_max = int(data[-1])

        elif data_title == "플레이시간" :
            data = data.replace("분", "").split("-")
            playTime_min = int(data[0])
            playTime_max = int(data[-1])

        elif data_title == "사용연령" :
            age = int(data.replace("세 이상", ""))

        elif data_title == "게임 난이도" :
            game_level = data.replace(" ", "").split("/")[0]

        else :
            print(data_title)

    # 분류, 테마
    categories = driver.find_elements_by_xpath('/html/body/div[3]/table//tr/td/table//tr/td/table[1]//tr[3]/td[1]/table//tr[2]/td/table//tr/td[2]/div/table//tr')
    before = ""
    for category in categories :
        if before == "분류" :
            genre = category.text.replace(" ", "").replace("\n", "&")
        elif before == "테마" :
            theme = category.text.replace(" ", "").replace("\n", "&")

        before = category.find_element_by_tag_name('td').text

        
    games.append({
        'ranking' : game['ranking'],
        'title' : game['title'],
        'title_eng' : title_eng,
        'year' : year,
        'genre' : genre,
        'people_min' : people_min,
        'people_max' : people_max,
        'playTime_min' : playTime_min,
        'playTime_max' : playTime_max,
        'age' : age,
        'theme' : theme,
        'game_level' : game_level
    })

driver.quit()

# csv 파일로 저장
with open('board_games.csv', 'w', encoding='utf-8-sig', newline='') as f :
    w = csv.DictWriter(f, fieldnames=games[0].keys())
    w.writeheader()
    for game in games :
        w.writerow(game)