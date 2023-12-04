from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NewsSerializer
import requests
import os
from bs4 import BeautifulSoup


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


def fetch_and_parse_article(html_content):
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


class PublicNewsFeedView(APIView):

    def get(self, request):
        news_links = get_all_news_links()
        articles_content = []

        for link in news_links:
            response = requests.get(link)
            if response.status_code == 200:
                article_content = fetch_and_parse_article(response.content)
                articles_content.append({'link': link, 'content': article_content})
            else:
                return Response({"message": f"Failed to fetch the article at {link}"},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(articles_content, status=status.HTTP_200_OK)
