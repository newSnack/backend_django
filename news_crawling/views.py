import json
import re
from datetime import datetime

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import News
from .serializers import NewsSerializer
import requests
import os
from bs4 import BeautifulSoup, SoupStrainer


# def extractNewsContent(url):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             return fetch_and_parse_article(response.content)
#         else:
#             return Response({'message': 'Failed to fetch the webpage'}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({'message': f'Error while fetching the webpage: {e}'},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# personal feed 영역

def getPersonalNaverSearch(node, srcText, start, display):
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


def contents_flat(c_List):
    flatList = []
    d_flatList = []
    for elem in c_List:
        if type(elem) == list:
            for e in elem:
                flatList.append(e)
        else:
            flatList.append(elem)

    return flatList


def get_comment(url):
    page = 1
    header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "referer": url,

    }
    oid = url.split("/")[-2]
    aid = url.split("/")[-1]
    c_List = []
    while True:
        c_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=100&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
            page) + "&refresh=false&sort=FAVORITE"
        r = requests.get(c_url, headers=header)
        cont = BeautifulSoup(r.content, "html.parser")
        total_comm = str(cont).split('comment":')[1].split(",")[0]

        match = re.findall('"contents":"([^\*]*)","userIdNo"', str(cont))
        date = re.findall('"modTime":"([^\*]*)","modTimeGmt"', str(cont))
        c_List.append(match)

        if int(total_comm) <= ((page) * 5):
            break
        else:
            page += 1

    return contents_flat(c_List)


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

    # Provider
    provider_strainer = SoupStrainer("a", attrs={"class": "media_end_head_top_logo _LAZY_LOADING_ERROR_HIDE"})
    provider_DOM = BeautifulSoup(document, "lxml", parse_only=provider_strainer)
    provider = provider_DOM.find("img")["alt"]

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
        "provider": provider
    }

    # Converting the dictionary to a JSON string
    json_data = json.dumps(data)
    return json_data


class PersonalNewsListView(APIView):

    def get(self, request):
        srcTexts = request.query_params.getlist('query')

        if not srcTexts:
            return Response({"message": "query empty."}, status=status.HTTP_400_BAD_REQUEST)

        jsonResult = []
        for srcText in srcTexts:
            jsonResponse = getPersonalNaverSearch('news', srcText, 1, 10)
            if jsonResponse:
                for cnt, post in enumerate(jsonResponse.get('items', []), 1):
                    # content = extractNewsContent(post['link'])
                    postData = {
                        'cnt': cnt,
                        'title': post['title'],
                        'description': post['description'],
                        'org_link': post['originallink'],
                        'link': post['link'],
                        'pDate': post['pubDate'],
                        # 'content': content
                    }
                    jsonResult.append(postData)
            else:
                return Response({"message": f"fail to make API request: {srcText}"},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = NewsSerializer(jsonResult, many=True)
        return Response(serializer.data)


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


def crawl_article_for_public(html_content): # 밑에 store 함수에 넘겨줄 기사 크롤링 담당
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


def store_crawled_public_article(): # 여러 기사 크롤링해서 News Object로 db에 저장. 비동기로 돌릴 예정
    news_links = get_all_news_links()
    for link in news_links:
        response = requests.get(link)
        if response.status_code == 200:
            article_content = crawl_article_for_public(response.content)
            News.objects.create(
                title=article_content['title'],
                description=article_content['description'],
                org_link=article_content['originallink'],
                link=link,
                pub_date=datetime.datetime.now(),
                content=article_content['content']
            )
        else:
            print(f"Failed to fetch the article at {link}")


class PublicNewsFeedView(APIView): # db에 저장해둔 public 뉴스 피드를 응답으로 보내는 view함수
    def get(self, request):
        news_data = News.objects.all()

        serializer = NewsSerializer(news_data, many=True)
        return Response(serializer.data)
