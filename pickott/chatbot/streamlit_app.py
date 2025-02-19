import streamlit as st
import requests

st.set_page_config(page_title="AI 챗봇")
st.title("🤖 AI 챗봇")

# API 엔드포인트
API_URL = "http://127.0.0.1:8000/chatbot/"

# 세션 상태 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
if user_input := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # API 호출
    response = requests.post(API_URL, json={"question": user_input})

    if response.status_code == 200:
        bot_reply = response.json()["answer"]
    else:
        bot_reply = "오류 발생: API 요청 실패"

    # 챗봇 응답 추가
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
