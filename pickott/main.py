import streamlit as st
import requests
from dotenv import load_dotenv
import os
from chatbot.chatbot import chat_call


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI 챗봇")
st.title("🤖 AI 챗봇")

# API 엔드포인트
API_URL = "http://127.0.0.1:8000/chatbot/"

# 세션 상태 저장
if "messages" not in st.session_state:
    st.session_state.messages = []


def signup():
    st.subheader("🔑 회원가입")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    email = st.text_input("email")

    if st.button("회원가입"):
        response = requests.post(f"{BASE_URL}/account/signup/", json={"username": username, "password": password, 'email':email})
        if response.status_code == 201:
            st.success("✅ 회원가입 성공! 이제 로그인하세요.")
        else:
            st.error("🚨 회원가입 실패! 다시 시도해주세요.")

def login():
    st.subheader("🔐 로그인")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        response = requests.post(f"{BASE_URL}/account/signin/", json={"username": username, "password": password})

        if response.status_code == 200:
            token = response.json().get("access")  # ✅ access_token 저장
            refresh_token = response.json().get("refresh")  # ✅ refresh_token 저장

            if not refresh_token:
                st.error("🚨 refresh_token을 받지 못했습니다! Django 로그인 API를 확인하세요.")
                return

            st.session_state["auth_token"] = token  # ✅ 세션에 저장
            st.session_state["refresh_token"] = refresh_token
            st.session_state["username"] = username

            st.success("✅ 로그인 성공!")
        else:
            st.error("🚨 로그인 실패! 아이디 또는 비밀번호를 확인하세요.")



def logout():
    if "auth_token" in st.session_state and "refresh_token" in st.session_state:
        headers = {"Authorization": f"Bearer {st.session_state['auth_token']}"}
        refresh_token = st.session_state.get("refresh_token", None)

        if not refresh_token:
            st.error("🚨 refresh_token이 존재하지 않습니다. 다시 로그인해 주세요.")
            return

        data = {"refresh": refresh_token}

        response = requests.post(f"{BASE_URL}/account/logout/", json=data, headers=headers)

        if response.status_code == 200:
            del st.session_state["auth_token"]
            del st.session_state["refresh_token"]
            del st.session_state["username"]
            st.success("✅ 로그아웃 되었습니다.")
        else:
            st.error(f"🚨 로그아웃 실패!")
    else:
        st.warning("🚨 로그인 상태가 아닙니다.")

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
    headers = {"Authorization": f"Bearer {st.session_state.get('auth_token', '')}"}  # 🔥 JWT 토큰 추가
    response = requests.post(API_URL, json={"question": user_input}, headers=headers)


    if response.status_code == 200:
        bot_reply = response.json()["answer"]
    else:
        bot_reply = "오류 발생: API 요청 실패"

    # 챗봇 응답 추가
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        


# 🔹 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["로그인", "회원가입", "챗봇"])

# 🔹 로그인 상태 확인
if "auth_token" in st.session_state:
    st.sidebar.write(f"✅ 로그인됨: {st.session_state['username']}")
    if st.sidebar.button("로그아웃"):
        logout()

# 🔹 메뉴 이동
if menu == "로그인":
    login()
elif menu == "회원가입":
    signup()