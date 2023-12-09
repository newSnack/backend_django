import json
import re
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response

from feed.models import PrivateFeed, PublicFeed
import requests
import os
from bs4 import BeautifulSoup, SoupStrainer

import openai
import re


openai.api_key = os.getenv("OPENAI_API_KEY")


# def contents_flat(c_List):
#     flatList = []
#     d_flatList = []
#     for elem in c_List:
#         if type(elem) == list:
#             for e in elem:
#                 flatList.append(e)
#         else:
#             flatList.append(elem)
#
#     return flatList
#
#
# def get_comment(url):
#     page = 1
#     header = {
#         "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
#         "referer": url,
#     }
#     oid = url.split("/")[-2]
#     aid = url.split("/")[-1]
#     c_List = []
#     while True:
#         c_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=100&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
#             page) + "&refresh=false&sort=FAVORITE"
#         r = requests.get(c_url, headers=header)
#         cont = BeautifulSoup(r.content, "html.parser")
#         total_comm = str(cont).split('comment":')[1].split(",")[0]
#
#         match = re.findall('"contents":"([^\*]*)","userIdNo"', str(cont))
#         c_List.append(match)
#
#         if int(total_comm) <= ((page) * 5):
#             break
#         else:
#             page += 1
#
#     return contents_flat(c_List)
def summarize_comments(comments):
    comments_combined = " ".join(comments)
    prompt = f"기사의 댓글들이다 두 세개의 문장으로 요약하고 각 문장을 쉼표로 구분해라: {comments_combined}"

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=60,
        temperature=0.5
    )

    # 요약된 텍스트 반환
    return response.choices[0].text.strip()


def get_comment(url):
    page = 1  # 첫 페이지만 조회
    header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "referer": url,
    }
    oid = url.split("/")[-2]
    aid = url.split("/")[-1]

    # 최대 10개 댓글만 조회
    c_url = f"https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news{oid}%2C{aid}&categoryId=&pageSize=10&indexSize=10&groupId=&listType=OBJECT&pageType=more&page={page}&refresh=false&sort=FAVORITE"
    response = requests.get(c_url, headers=header)
    content = BeautifulSoup(response.content, "html.parser")

    total_comm = str(content).split('comment":')[1].split(",")[0]

    if int(total_comm) > 0:
        matches = re.findall('"contents":"([^\*]*)","userIdNo"', str(content))
        summarized_comments = summarize_comments(matches)
        return summarized_comments.split(',')  # 쉼표로 분리하여 리스트 반환
    else:
        return []  # 댓글이 없는 경우 빈 리스트 반환


def convert_string_to_datetime(date_string):
    match = re.match(r'(\d{4}.\d{2}.\d{2}.) (오전|오후) (\d{1,2}:\d{2})', date_string)
    
    if match:
        date_part, am_pm, time_part = match.groups()

        if am_pm == '오후':
            # 오후인 경우 12를 더해서 24시간 형식으로 변환
            time_part = datetime.strptime(time_part, '%I:%M').strftime('%H:%M')
            hours, minutes = map(int, time_part.split(':'))
            if hours < 12:
                hours += 12
            time_part = f'{hours:02d}:{minutes:02d}'

        datetime_string = f'{date_part} {time_part}'
        dt_object = datetime.strptime(datetime_string, '%Y.%m.%d. %H:%M')
        return dt_object
    else:
        raise ValueError("올바르지 않은 형식의 문자열입니다.")


def additional_article_info(url: str):
    headers = {
        'authority': 'n.news.naver.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ko-KR,ko;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    response = requests.get(url, headers=headers)
    document = response.content.decode("utf-8")

    # Date
    date_strainer = SoupStrainer("span", attrs={"class": "media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"})
    date_DOM = BeautifulSoup(document, "lxml", parse_only=date_strainer)
    date = date_DOM.get_text(separator="\n").strip()

    # img
    try:
        img_strainer = SoupStrainer("div", attrs={"class": "media_end_photo_photo"})
        img_DOM = BeautifulSoup(document, "lxml", parse_only=img_strainer)
        img = img_DOM.find("img")["src"]
    except:
        img = "NO_IMAGE"

    comment = get_comment(url)
    data = {
        "comment": comment,
        "img": img,
        "date": convert_string_to_datetime(date),
        "category": int(url.split("/")[-2])
    }

    # Converting the dictionary to a JSON string
    return data


def get_personal_naver_search(node, srcText, start, display):
    client_id = os.environ.get('NAVER_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET')

    base = "https://openapi.naver.com/v1/search"
    node = f"/{node}.json"
    parameters = f"?query={requests.utils.quote(srcText)}&start={start}&display={display}"

    url = base + node + parameters
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


def generate_search_queries(keywords):
    prompt = (
            "다음 키워드들을 연관성이 있는 그룹으로 분류하고, 각 그룹에 대한 효과적인 뉴스 검색 쿼리를 한국어로 생성해라. "
            "각 검색 쿼리는 개행 문자로 구분해라. 키워드들: " + ", ".join(keywords)
    )

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7  # 창의적인 답변을 위한 설정, 필요에 따라 조절 가능
    )

    return response.choices[0].text.strip().split('\n')


def store_crawled_personal_article(user):
    generated_queries = generate_search_queries(user.interest_keywords)
    all_feeds = []

    for query in generated_queries:
        jsonResponse = get_personal_naver_search('news', query, 1, 10)
        if jsonResponse:
            for post in jsonResponse.get('items', []):
                additional_info = additional_article_info(post['link'])
                feed = {
                    'user': user,
                    'title': post['title'],
                    'content': post['description'],
                    'comment': additional_info['comment'],
                    'originalURL': post['link'],
                    'date': additional_info['date'],
                    'imgURL': additional_info['img'],
                    'likeOrDislike': 0,
                }
                all_feeds.append(feed)
        else:
            print(f"Failed to make API request for query: {query}")

    # 최신순으로 정렬
    sorted_feeds = sorted(all_feeds, key=lambda x: x['date'], reverse=True)
    for feed in sorted_feeds:
        PrivateFeed.objects.create(**feed)


# public feed 영역
def get_all_news_links():
    sid1_sid2_combinations = [
        ('105', ['732', '731', '230', '283', '228', '229']),
        ('104', ['231', '232', '233', '234']),
        ('103', ['237', '238', '239', '241', '248', '376']),
        ('102', ['249', '250', '251', '252', '254', '255']),
        ('101', ['258', '259', '260', '261', '262', '771']),
        ('100', ['264', '265', '266', '267', '268'])
    ]

    all_news_links = []

    for sid1, sid2_list in sid1_sid2_combinations:
        for sid2 in sid2_list:
            url = f"https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1={sid1}&sid2={sid2}"
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                news_ul = soup.find('ul', class_='type06_headline')
                if news_ul:
                    link = news_ul.find('li').find('a')
                    if link and link.has_attr('href'):
                        all_news_links.append(link['href'])
                    # list_items = news_ul.find_all('li')[:2]
                    # for item in list_items:
                    #     link = item.find('a')
                    #     if link and link.has_attr('href'):
                    #         all_news_links.append(link['href'])
    return all_news_links


def crawl_article_for_public(html_content):  # 밑에 store 함수에 넘겨줄 기사 크롤링 담당
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        article_content_div = soup.find('article', id='dic_area')

        image_description = article_content_div.find('div', class_='end_photo_org')
        if image_description:
            image_description.extract()

        media_summary = article_content_div.find('strong', class_='media_end_summary')
        if media_summary:
            media_summary.extract()

        news_content = article_content_div.get_text(strip=True) if article_content_div else 'No content available'
        return news_content
    except Exception as e:
        return Response({'message': f'Error while fetching news content: {e}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def store_crawled_public_article():  # 여러 기사 크롤링해서 Feed Object로 db에 저장. 비동기로 돌릴 예정
    news_links = get_all_news_links()
    for link in news_links:
        response = requests.get(link)
        if response.status_code == 200:
            article_content = crawl_article_for_public(response.content)
            additional_info = additional_article_info(link)

            summarized_comments = summarize_comments(additional_info['comment'])
            summarized_comments_str = ', '.join(summarized_comments)

            PublicFeed.objects.create(
                title=article_content['title'][:30],
                content=article_content['content'],
                comment=summarized_comments_str,
                originalURL=link,
                # date
                imgURL=additional_info['img'],
            )
        else:
            print(f"Failed to fetch the article at {link}")
