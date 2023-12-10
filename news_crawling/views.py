import json
import re
from datetime import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status, request
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
    messages = [
        {"role": "system", "content": "댓글을 요약할 수 있는 도우다."},
        {"role": "user", "content": f"이 댓글들을 두 세 문장으로 요약해라 단, 어투를 그대로 유지해라: {comments_combined}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=60
    )

    return response["choices"][0]["message"]["content"].strip()


def summarize_article(article):
    messages = [
        {"role": "system", "content": "기사를 요약할 수 있는 도우미다."},
        {"role": "user", "content": f"이 기사를 핵심만 세네 문장으로 요약해라: {article}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200
    )

    return response["choices"][0]["message"]["content"].strip()


def get_comment(url):
    page = 1  # 첫 페이지만 조회
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "referer": url,
    }
    oid = url.split("/")[-2]
    aid = url.split("/")[-1]

    c_url = f"https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news{oid}%2C{aid}&categoryId=&pageSize=10&indexSize=10&groupId=&listType=OBJECT&pageType=more&page={page}&refresh=false&sort=FAVORITE"
    response = requests.get(c_url, headers=headers)
    content = BeautifulSoup(response.content, "html.parser")

    if 'comment":' in str(content):
        total_comm = str(content).split('comment":')[1].split(",")[0]
        if int(total_comm) > 0:
            matches = re.findall('"contents":"([^\*]*)","userIdNo"', str(content))
            summarized_comments = summarize_comments(matches)
            return summarized_comments.split(',')
        else:
            return []
    else:
        return []


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
    try:
        document = response.content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            document = response.content.decode("euc-kr")
        except UnicodeDecodeError:
            return {"error": "Decoding failed"}

    # Date
    # date_strainer = SoupStrainer("span", attrs={"class": "media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"})
    # date_DOM = BeautifulSoup(document, "lxml", parse_only=date_strainer)
    # date = date_DOM.get_text(separator="\n").strip()

    # img
    img_soup = BeautifulSoup(document, 'lxml').find_all('img')
    img = 'NO_IMAGE'
    for img in img_soup:
        if img.get('id'):
            img = img.get('data-src')
            break

    # category
    pattern = r'section\s*=\s*{([^}]*)}'
    match = re.search(pattern, document)

    if match:
        data_dict = json.loads('{' + match.group(1) + '}')
        category = data_dict.get("name", "NO_CATEGORY")
    else:
        category = "NO_CATEGORY"

    comment = get_comment(url)
    data = {
        "comment": comment,
        "img": img,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category
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
    prompt = "다음은 유저가 검색한 기사 제목들이다. 이들에 기반해 유저가 추후 관심있어할 뉴스기사에 포함될 단어들을 몇개 나열하고 쉼표로 구분하라. 답변은 반드시 순수 한글 단어나 구만 반드시 쉼표로 구분해서 나열하고 절대 다른 쓸데없는 말은 포함하지마라" + \
             "기사제목들: " + ", ".join(keywords)

    messages = [
        {"role": "system", "content": "유저가 검색한 기사 제목들에 기반해 관심있어할만한 뉴스 기사에 포함될 단어들을 유추하는 도우미."},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100
    )

    return response["choices"][0]["message"]["content"].strip().split(',')


User = get_user_model()

import logging

logging.basicConfig(level=logging.INFO)


def store_crawled_personal_article(request):
    username = request.GET.get('username')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

    generated_queries = generate_search_queries(user.interest_keywords)

    logging.info(f"Generated queries: {generated_queries}")

    for query in generated_queries:
        jsonResponse = get_personal_naver_search('news', query, 1, 1)
        if jsonResponse:
            for post in jsonResponse.get('items', []):
                additional_info = additional_article_info(post['link'])
                if "error" in additional_info:
                    logging.error(f"Error fetching article info: {additional_info['error']}")
                    continue
                logging.info(f"Fetching article {post['title']}")
                summarized_comments = summarize_comments(additional_info['comment'])
                summarized_comments_str = ', '.join(summarized_comments)
                img = additional_info.get('img', 'NO_IMAGE')

                feed_data = {
                    'user': user,
                    'title': post['title'],
                    'content': post['description'],
                    'comment': summarized_comments_str,
                    'originalURL': post['link'],
                    'imgURL': img,
                    'date': additional_info['date'],
                    'likeOrDislike': 0,
                    'category': additional_info['category']
                }

                PrivateFeed.objects.create(**feed_data)
        else:
            logging.error(f"Failed to make API request for query: {query}")

    return HttpResponse("Crawling and data processing completed successfully.")


# public feed 영역
def get_all_news_links():
    sid1_sid2_combinations = [
        ('105', ['732', '731', '230', '228']),
        ('104', ['231', '232', '233', '234']),
        ('103', ['237', '238', '239', '241']),
        ('102', ['249', '250', '251', '252']),
        ('101', ['258', '259', '260', '261']),
        ('100', ['264', '265', '266', '267'])
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
                    list_items = news_ul.find_all('li', limit=1)
                    for item in list_items:
                        link = item.find('a')
                        if link and link.has_attr('href'):
                            all_news_links.append(link['href'])
    return all_news_links


def crawl_article_for_public(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 제목 추출
        title_area = soup.find('h2', id='title_area')
        if title_area and title_area.span:
            title = title_area.span.get_text(strip=True)
        else:
            title = 'No title available'

        # 기사 내용 추출
        article_content_div = soup.find('article', id='dic_area')
        if article_content_div:
            image_description = article_content_div.find('div', class_='end_photo_org')
            if image_description:
                image_description.extract()

            media_summary = article_content_div.find('strong', class_='media_end_summary')
            if media_summary:
                media_summary.extract()

            news_content = article_content_div.get_text(strip=True)


        else:
            news_content = 'No content available'

        return {
            'title': title,
            'content': news_content
        }
    except Exception as e:
        return {'title': 'Error', 'content': f'Error while fetching news content: {e}'}


import logging

logging.basicConfig(level=logging.INFO)


def store_crawled_public_article(request):
    try:
        logging.info("Crawling started.")
        news_links = get_all_news_links()
        for link in news_links:
            response = requests.get(link)
            if response.status_code == 200:
                logging.info(f"Fetching article from {link}")
                article_content = crawl_article_for_public(response.content)
                additional_info = additional_article_info(link)

                # summarized_comments = summarize_comments(additional_info['comment'])
                # summarized_comments_str = ', '.join(summarized_comments)

                summarized_article_str = summarize_article(article_content['content'])

                PublicFeed.objects.create(
                    title=article_content['title'][:30],
                    content=summarized_article_str,
                    # comment=summarized_comments_str,
                    originalURL=link,
                    date=additional_info['date'],
                    imgURL=additional_info['img'],
                    category=additional_info['category'],
                )
            else:
                logging.error(f"Failed to fetch the article at {link}")
                print(f"Failed to fetch the article at {link}")

        return HttpResponse("Crawling and data processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return HttpResponse(f"An error occurred: {e}", status=500)
