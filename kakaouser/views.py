
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect
from django.http import JsonResponse
import json
from json import JSONDecodeError
from rest_framework import status
import os
import requests
from user.models import User
from django.conf import settings

from user.embeddings import get_user_interest_embedding, get_article_embeddings, find_closest_articles
from feed.models import PrivateFeed
from datetime import datetime

BASE_URL = 'http://localhost:8000/'
KAKAO_CALLBACK_URI = 'http://localhost:5173/api/kuser/kakao/callback/'


def refresh_access_token(refresh_token):
    payload = {
        'grant_type': 'refresh_token',
        'client_id': settings.KAKAO_APP_KEY,
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }

    try:
        response = requests.post('https://kauth.kakao.com/oauth/token', headers=headers, data=payload)

        if response.status_code == 200:
            new_access_token = response.json().get('access_token')
            new_refresh_token = response.json().get('refresh_token')
            return new_access_token
        else:
            error_message = response.json().get('error_description', 'Unknown error')
            print(f"Error refreshing token: {error_message}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during token refresh request: {e}")
        return None


def send_to_me(request):
    access_token = request.GET.get('access_token')
    refresh_token = request.GET.get('refresh_token')

    validation_response = requests.get('https://kapi.kakao.com/v1/user/access_token_info',
                                       headers={'Authorization': f'Bearer {access_token}'})
    # 액세스 토큰 만료시 재발급
    if validation_response.status_code != 200:
        new_access_token = refresh_access_token(refresh_token)
        if new_access_token:
            access_token = new_access_token
        else:
            return JsonResponse({'status': 'error', 'message': 'Refresh token expired'})

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    user_info_response = requests.get('https://kapi.kakao.com/v2/user/me', headers=headers)
    if user_info_response.status_code != 200:
        return JsonResponse({'status': 'error', 'message': 'Failed to get user information from Kakao'})

    kakao_user_info = user_info_response.json()
    kakao_email = kakao_user_info.get('kakao_account', {}).get('email')  # 카카오 사용자 고유 이메일

    # Django 사용자 인스턴스 매핑
    try:
        user = User.objects.get(kakaoAddress=kakao_email)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found in Django'})

    # 기사 추천 알고리즘 실행
    user_interests = user.interest_keywords
    user_embedding = get_user_interest_embedding(user_interests)
    articles_embeddings = get_article_embeddings(user)
    closest_titles = find_closest_articles(user_embedding, articles_embeddings)
    closest_articles = PrivateFeed.objects.filter(title__in=closest_titles, user=user, date=datetime.today().date())

    # 추천된 기사를 템플릿 객체에 포함
    articles_content = []
    for article in closest_articles:
        articles_content.append(f"{article.title}: {article.content}")

    template_object = {
        "object_type": "feed",
        "content": {
            "title": "Personalized News Update",
            "description": "\n".join(articles_content),
        }
    }

    payload = {
        'template_object': json.dumps(template_object),
    }

    # 메시지 전송
    response = requests.post(
        'https://kapi.kakao.com/v2/api/talk/memo/default/send',
        headers=headers,
        data=payload
    )

    if response.status_code == 200:
        return JsonResponse({'status': 'success', 'message': 'Message sent successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to send message'})


# 인가코드는 프론트에서 받는 걸로 변경하기
def kakao_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code")


def kakao_callback(request, **kwargs):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    code = kwargs['code']

    # code로 access token 요청
    token_request = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
    token_response_json = token_request.json()

    print("response=>", token_response_json)

    # 에러 발생 시 중단
    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_response_json.get("access_token")

    # access token으로 카카오톡 프로필 요청
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    kakao_account = profile_json.get("kakao_account")
    username = kakao_account.get("nickname", None)

    # 해당 이메일 유저가 있나 확인
    try:
        # 전달받은 닉네임으로 등록된 유저가 있는지 탐색
        user = User.objects.get(username=username)
        # FK로 연결되어 있는 socialaccount 테이블에서 해당 닉네임의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)

        # 있는데 카카오계정이 아니어도 에러
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 카카오로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/kuser/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        print("accept=>", accept)

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        # accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        # 전달받은 닉네임으로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/kuser/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        print(accept)

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()

        return JsonResponse(accept_json)

    except SocialAccount.DoesNotExist:
        # User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
        return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client
