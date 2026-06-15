"""
카카오톡 '나에게 메시지 보내기' 스크립트
- access_token이 만료되었을 경우 refresh_token으로 자동 갱신
"""

import os
import requests

REST_API_KEY = os.environ["KAKAO_REST_API_KEY"]
ACCESS_TOKEN = os.environ["KAKAO_ACCESS_TOKEN"]
REFRESH_TOKEN = os.environ["KAKAO_REFRESH_TOKEN"]

TOKEN_URL = "https://kauth.kakao.com/oauth/token"
SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

MESSAGE_TEXT = "카카오톡 자동 알림 메시지입니다."
MESSAGE_LINK = "https://www.kakao.com"


def refresh_access_token(refresh_token):
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": REST_API_KEY,
            "refresh_token": refresh_token,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def send_message(access_token):
    template_object = {
        "object_type": "text",
        "text": MESSAGE_TEXT,
        "link": {"web_url": MESSAGE_LINK, "mobile_web_url": MESSAGE_LINK},
    }
    resp = requests.post(
        SEND_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": str(template_object).replace("'", '"')},
        timeout=10,
    )
    return resp


def main():
    access_token = ACCESS_TOKEN
    new_tokens = None

    resp = send_message(access_token)

    if resp.status_code == 401:
        print("access_token이 만료되었습니다. refresh_token으로 갱신을 시도합니다.")
        new_tokens = refresh_access_token(REFRESH_TOKEN)
        access_token = new_tokens["access_token"]
        resp = send_message(access_token)

    resp.raise_for_status()
    print("메시지 전송 결과:", resp.json())

    if new_tokens:
        print("\n=== 새 토큰이 발급되었습니다. GitHub Secrets를 업데이트하세요 ===")
        print("KAKAO_ACCESS_TOKEN =", new_tokens["access_token"])
        if "refresh_token" in new_tokens:
            print("KAKAO_REFRESH_TOKEN =", new_tokens["refresh_token"])

        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write(f"new_access_token={new_tokens['access_token']}\n")
                if "refresh_token" in new_tokens:
                    f.write(f"new_refresh_token={new_tokens['refresh_token']}\n")
                f.write("token_updated=true\n")


if __name__ == "__main__":
    main()
