class Config:
    # 지역 검색의 라우터 호출 경로
    ROUTER_API = 'https://clovastudio.stream.ntruss.com/v1/routers/k6mdhbkh/versions/1/route'

    # 지역 검색 스킬셋 호출 경로
    SKILLSET_API = 'https://clovastudio.stream.ntruss.com/v1/skillsets/stocub8o/versions/1/final-answer'

    # 지역 검색 스킬셋에 정의된 스킬(API)의 인증 정보
    NAVER_LOCAL_CLIENT_ID = 'hLHF9A32OOjvD_U1dkFS'
    NAVER_LOCAL_CLIENT_SECRET = 'p58pvyUGT6'

    # Chat Completions 호출 경로
    CHAT_COMPLETIONS_API = 'https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003'

    # CLOVA Studio API 인증 정보
    API_KEY = 'nv-ebd40d0c9f3e47db868dd96d55e6a5c0P2nZ'
    REQUEST_ID_ROUTER = '13df804282bb48c4ae537c2dcef68d5e'
    REQUEST_ID_SKILLSET = '5cb26d6f57ae4799b65ffa6744421df6'
    REQUEST_ID_CHAT = '1234'