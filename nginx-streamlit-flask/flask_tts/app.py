# tts_server.py (수정된 Flask 코드)
from flask import Flask, request, Response
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)

#.env 파일 로드(컨테이너 내부 경로 기준)
#dockerfile에서 WORKDIR /app 을 했기에 기본 경로가 아래와 같음
load_dotenv(dotenv_path="/app/.env")

# 네이버 클라우드 API 인증 정보 (환경 변수로 관리)
# os.environ['NCP_CLOVASTUDIO_APP_ID']와 같이 환경 변수를 설정해주세요.
CLIENT_ID = os.environ.get("NCP_CLOVASTUDIO_APP_ID")
CLIENT_SECRET = os.environ.get("NCP_CLOVASTUDIO_APP_SECRET")

# TTS 처리 라우팅
@app.route('/tts', methods=['POST'])
def speak():
    data = request.json  # JSON 형식으로 데이터 받기
    if not data:
        return "Invalid JSON", 400

    text = data.get('text', '')
    speaker = data.get('speaker', 'nara')

    if not text:
        return "텍스트를 입력해주세요", 400

    # TTS API 요청
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    tts_data = {
        "speaker": speaker,
        "speed": "0",
        "text": text
    }

    response = requests.post(url, headers=headers, data=tts_data)

    if response.status_code == 200:
        return Response(
            response.content,
            mimetype="audio/mpeg"
        )
    else:
        return f"오류 발생: {response.status_code} {response.text}", response.status_code

if __name__ == '__main__':
    # 환경 변수가 설정되었는지 확인
    if not CLIENT_ID or not CLIENT_SECRET:
        print("경고: 환경 변수 'NCP_CLOVASTUDIO_APP_ID' 또는 'NCP_CLOVASTUDIO_APP_SECRET'이(가) 설정되지 않았습니다.")
    
    app.run(port=5000, debug=True)
