import requests
from config import Config


def get_router(query, chat_history=None):
    url = Config.ROUTER_API
    headers = {
        'Authorization': f'Bearer {Config.API_KEY}',
        'X-NCP-CLOVASTUDIO-REQUEST-ID': f'{Config.REQUEST_ID_ROUTER}',
        'Content-Type': 'application/json'
    }
    data = {
        'query': query
    }

    if chat_history and len(chat_history) >= 3:
        # 직전 user 턴의 발화를 가져옵니다.
        filtered_chat_history = chat_history[-3]
        data['chatHistory'] = [filtered_chat_history]

    response = requests.post(url, headers=headers, json=data)
    #print(response.json())
    return response.json()