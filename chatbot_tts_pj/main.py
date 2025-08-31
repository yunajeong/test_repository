# main.py (수정된 Streamlit 코드)
import streamlit as st
import requests, base64
from router import get_router
from chat_utils import streaming_data
from chat_completions import get_chat_response
from skillset import get_skillset

# Flask 서버 URL 설정
TTS_SERVER_URL = "http://localhost:5000/tts"

# TTS 음성 종류 옵션 (NCP TTS 모델에 따라 변경 가능)
VOICE_OPTIONS = {
    "남성 목소리 - 진호": "jinho",
    "여성 목소리 - 나라": "nara",
    "여성 목소리 - 혜리": "nes_c_hyeri"
}

def initialize_chat_session():
    """에이전트 세션 초기화"""
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                'role': 'assistant',
                'content': '안녕하세요. 장소 탐색 AI Agent입니다.😃 \n\n어떤 곳을 찾고 계신가요? 궁금하신 장소 정보가 있다면 언제든지 말씀해 주세요.'
            }
        ]

def render_initial_messages():
    """메시지 렌더링"""
    with st.chat_message(st.session_state.messages[0]['role']):
        st.write(st.session_state.messages[0]['content'])

    for message in st.session_state.messages[1:]:
        with st.chat_message(message['role']):
            st.write(message['content'])

def display_response(final_answer):
    """응답 표시 및 세션 상태 업데이트"""
    with st.chat_message('assistant'):
        st.write_stream(streaming_data(final_answer))
    st.session_state.messages.append({'role': 'assistant', 'content': final_answer})

def process_router(query, chat_history):
    """라우터 호출"""
    with st.status("라우터 적용 중...", expanded=True) as router_status:
        process_view = st.empty()
        process_view.write("라우터 적용 중입니다.")
        router_result = get_router(query, chat_history)
        domain = router_result.get('result', {}).get('domain', {}).get('result', '')
        blocked_content = router_result.get('result', {}).get('blockedContent', {}).get('result', [])
        safety = router_result.get('result', {}).get('safety', {}).get('result', [])
    return domain, blocked_content, safety, router_status, process_view

def generate_skillset_response(query, chat_history):
    """지역 검색 스킬셋 응답 생성"""
    with st.status("답변 생성 중...", expanded=True) as answer_status:
        process_view = st.empty()
        process_view.write("API를 호출하고 답변을 생성하는 중입니다. 잠시만 기다려주세요.")
        result = get_skillset(query, chat_history)
        final_answer = result.get('result', {}).get('finalAnswer', '답변을 생성할 수 없습니다.')
        process_view.write("답변 생성이 완료되었습니다.")
        answer_status.update(label="답변 생성 완료", state="complete", expanded=False)
    return final_answer

def generate_chat_response(query, chat_history):
    """chat_completions 응답 생성"""
    with st.status("답변 생성 중...", expanded=True) as answer_status:
        process_view = st.empty()
        process_view.write("요청하신 내용에 대한 답변을 생성 중입니다. 잠시만 기다려주세요.")
        result = get_chat_response(query, chat_history)
        final_answer = result.get('result', {}).get('message', {}).get('content', '답변을 생성할 수 없습니다.')
        process_view.write("답변 생성이 완료되었습니다.")
        answer_status.update(label="답변 생성 완료", state="complete", expanded=False)
    return final_answer

def generate_filtered_response(filter_type):
    """고정 응답"""
    if filter_type == 'content':
        return "**콘텐츠 필터 규정**에 따라, 해당 질문에는 답변을 제공해 드리기 어려운 점 양해 부탁드려요.\n\n" \
               "혹시 이렇게 질문해 보시는 건 어떠실까요? :)\n" \
               "- 경기도 가을 단풍 명소 추천해 주세요.\n" \
               "- 제주도 애월 맛집과 카페"
    else:  # safety filter
        return '**안전 관련 규정**에 따라, 해당 질문에는 답변을 제공해 드리기 어려운 점 양해 부탁드려요.\n\n' \
               '혹시 이렇게 질문해 보시는 건 어떠실까요?\n' \
               '- 부산에서 인기 있는 맛집 찾아줄래?\n' \
               '- 서울 분위기 좋은 카페 추천\n' \
               '- 티엔미미 인기 메뉴 알려주세요\n\n' \
               '언제나 좋은 정보로 도움 드리고자 합니다. 필요하신 내용이 있으시면 편하게 말씀해 주세요! 😊'

def play_tts_audio(text_to_speak, voice_name):
    """Flask 서버에 TTS 요청을 보내고 오디오 재생"""
    try:
        response = requests.post(
            TTS_SERVER_URL,
            json={"text": text_to_speak, "speaker": voice_name},  # speaker 파라미터 사용
            stream=True
        )


        #response.raise_for_status()
        
        # 오디오 데이터를 세션 상태에 저장 - 변경전
        # st.session_state.tts_audio = response.content
        # st.audio(st.session_state.tts_audio, format='audio/mpeg')
        #------------------------------------------------------------
        # 응답 상태 코드 확인 로직 추가
        if response.status_code == 200:
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            audio_html = f"""
                <audio autoplay controls>
                    <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        else:
            # 오류가 발생한 경우 오류 메시지를 출력
            st.error(f"음성 변환 서버 오류: {response.status_code} {response.text}")

        #------------------------------------------------------------
    except requests.exceptions.RequestException as e:
        st.error(f"음성 변환 서버 오류: {e}")

def main():
    st.set_page_config(page_title="장소 탐색 에이전트")
    st.title('장소 탐색 에이전트', anchor=False)
    st.write(' ')

    # 사이드바에 TTS 옵션 추가
    with st.sidebar:
        st.header("음성 설정")
        selected_voice_label = st.selectbox("음성 종류 선택", list(VOICE_OPTIONS.keys()))
        selected_voice_name = VOICE_OPTIONS[selected_voice_label]
        
        # 마지막 챗봇 답변을 가져와서 TTS 재생
        if st.button("답변 음성으로 듣기 🔊"):
            if st.session_state.messages and st.session_state.messages[-1]['role'] == 'assistant':
                last_assistant_message = st.session_state.messages[-1]['content']
                if last_assistant_message:
                    with st.spinner("음성 생성 중..."):
                        play_tts_audio(last_assistant_message, selected_voice_name)
            else:
                st.warning("먼저 답변을 생성해 주세요.")

    initialize_chat_session()
    render_initial_messages()

    if query := st.chat_input('질문을 입력하세요.'):
        with st.chat_message('user'):
            st.write(query)
        st.session_state.messages.append({'role': 'user', 'content': query})
        
        chat_history = [{'role': msg['role'], 'content': msg['content']} for msg in st.session_state.messages]
        domain, blocked_content, safety, router_status, process_view = process_router(query, chat_history)

        router_status.update(label="라우터 적용 중...", state="running", expanded=True)

        if domain == "지역 검색":
            if not blocked_content and not safety:
                process_view.write("지역 검색 스킬셋으로 처리 가능합니다.")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_skillset_response(query, chat_history)
                display_response(final_answer)
            elif blocked_content and not safety:
                process_view.write("스킬셋 사용이 불가능합니다. (이유 : 콘텐츠 필터)")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_filtered_response('content')
                display_response(final_answer)
            else:
                process_view.write("스킬셋 사용이 불가능합니다. (이유 : 세이프티 필터)")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_filtered_response('safety')
                display_response(final_answer)
        else:
            process_view.write("스킬셋과 관련 없는 요청입니다.")
            router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
            final_answer = generate_chat_response(query, chat_history)
            display_response(final_answer)

if __name__ == '__main__':
    main()