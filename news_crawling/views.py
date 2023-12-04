from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NewsSerializer
import requests
import os
from bs4 import BeautifulSoup

def getNewsContent(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            content_div = soup.find('div', id='ijam_content')
            news_content = content_div.get_text(strip=True) if content_div else '내용이 없습니다.'
            return news_content
        else:
            return None
    except Exception as e:
        print(f"Error while fetching news content: {e}")
        return None

def getNaverSearch(node, srcText, start, display):
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
      
class NewsListView(APIView):
    def get(self, request, format=None):
        srcText = request.query_params.get('query', None)
        if srcText is None:
            return Response({"message": "검색어를 입력하세요."})

        jsonResponse = getNaverSearch('news', srcText, 1, 100)
        if jsonResponse is None:
            return Response({"message": "API 요청에 실패했습니다."})

        jsonResult = []
        for cnt, post in enumerate(jsonResponse.get('items', []), 1):
            content = getNewsContent(post['link'])
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

        serializer = NewsSerializer(jsonResult, many=True)
        return Response(serializer.data)
