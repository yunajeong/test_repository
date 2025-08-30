from flask import Flask, request, render_template, Response
import requests

app = Flask(__name__)

# 네이버 클라우드 API 인증 정보
CLIENT_ID = "fz7gbkpe0n"       
CLIENT_SECRET = "R3pXWNHDIxTRwKkz33m9COR5Ia6fDcNbAqRKeXO9"  

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/speak', methods=['POST'])
def speak():
    text = request.form.get('text', '')

    if not text:
        return "텍스트를 입력해주세요", 400

    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    speaker = request.form.get('speaker', 'nara')
    data = {
        "speaker": speaker,  # 화자
        "speed": "0",       # 속도 (-5~5)
        "text": text
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        # 파일 저장 없이 바로 브라우저로 전송
        return Response(
            response.content,
            mimetype="audio/mpeg"
        )
    else:
        return f"오류 발생: {response.status_code} {response.text}", response.status_code

if __name__ == '__main__':
    app.run(debug=True)
