from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NewsSerializer
import requests
import os
from bs4 import BeautifulSoup


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


def getPersonalNewsContent(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return fetch_and_parse_article(response.content)
        else:
            return Response({'message': 'Failed to fetch the webpage'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': f'Error while fetching the webpage: {e}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
            return Response({"message": "검색어가 없거나 비어있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        jsonResult = []
        for srcText in srcTexts:
            jsonResponse = getPersonalNaverSearch('news', srcText, 1, 10)  # Fetch only 10 articles
            if jsonResponse:
                for cnt, post in enumerate(jsonResponse.get('items', []), 1):
                    content = getPersonalNewsContent(post['link'])
                    postData = {
                        'cnt': cnt,
                        'title': post['title'],
                        'description': post['description'],
                        'org_link': post['originallink'],
                        'link': post['link'],
                        'pDate': post['pubDate'],
                        'content': content
                    }
                    jsonResult.append(postData)
            else:
                return Response({"message": f"API 요청에 실패했습니다: {srcText}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = NewsSerializer(jsonResult, many=True)
        return Response(serializer.data)
