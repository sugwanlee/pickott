import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PickOtt")
st.title("🤖 AI 피콧")

# API 엔드포인트
API_URL = "http://127.0.0.1:8000/chatbot/"

# 세션에 대화 기록 저장 저장
if "messages" not in st.session_state:
    st.session_state.messages = []


# 회원가입
def signup():
    st.subheader("🔑 회원가입")

    # 🔹 세션 상태 초기화 (없을 경우만)
    st.session_state.setdefault("signup_username", "")
    st.session_state.setdefault("signup_password", "")
    st.session_state.setdefault("signup_email", "")

    # 🔹 입력 필드 (세션 상태와 연동)
    username = st.text_input("아이디", key="signup_username")
    password = st.text_input("비밀번호", type="password", key="signup_password")
    email = st.text_input("이메일", key="signup_email")

    if st.button("회원가입"):
        # DRF 회원 가입 로직에 요청
        signup_response = requests.post(
            f"{BASE_URL}/account/signup/",
            json={"username": username, "password": password, "email": email},
        )

        # 회원가입 후에 자동으로 로그인 진행
        if signup_response.status_code == 201:
            st.success("✅ 회원가입 성공! 자동 로그인 중...")

            # 🔹 회원가입 성공 후 자동 로그인 요청
            login_response = requests.post(
                f"{BASE_URL}/account/signin/",
                json={"username": username, "password": password},
            )

            # 로그인 성공 로직
            if login_response.status_code == 200:
                data = login_response.json()
                # access_token 및 refresh token 을 session에 저장
                st.session_state["auth_token"] = data.get("access")
                st.session_state["refresh_token"] = data.get("refresh")
                # usernmae = id 를 session에 저장
                st.session_state["username"] = username

                st.success(f"✅ {username}님 환영합니다! 챗봇 화면으로 이동합니다.")

                # 🔹 로그인 성공 → 챗봇 화면으로 이동
                st.session_state["menu"] = "챗봇"
                st.rerun()
            # 로그인 실패 시
            else:
                st.error("🚨 자동 로그인 실패! 로그인 화면으로 이동하세요.")
                st.session_state["menu"] = "로그인"
                st.rerun()
        # 회원 가입 실패
        else:
            st.error("🚨 회원가입 실패! 다시 시도해주세요.")


# 로그인 기능
def login():
    st.subheader("🔐 로그인")

    # 필요 데이터 전달
    username = st.text_input("아이디", key="login_username")
    password = st.text_input("비밀번호", type="password", key="login_password")

    if st.button("로그인"):
        # DRF 로그인 API에 요청
        response = requests.post(
            f"{BASE_URL}/account/signin/",
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            data = response.json()
            # access_token 및 refresh token 을 session에 저장
            st.session_state["auth_token"] = data.get("access")
            st.session_state["refresh_token"] = data.get("refresh")
            # usernmae = id 를 session에 저장
            st.session_state["username"] = username

            st.success("✅ 로그인 성공!")
            # 챗봇 화면으로 전환
            st.rerun()  # UI 갱신
        else:
            st.error("🚨 로그인 실패! 아이디 또는 비밀번호를 확인하세요.")


# 로그아웃 기능
def logout():
    # token 두 개가 session에 있을 때만 실행
    if "auth_token" in st.session_state and "refresh_token" in st.session_state:
        # acces token 과 refresh toekn을 담아 DRF 로그아웃 API에 요청
        headers = {"Authorization": f"Bearer {st.session_state['auth_token']}"}
        data = {"refresh": st.session_state["refresh_token"]}

        response = requests.post(
            f"{BASE_URL}/account/logout/", json=data, headers=headers
        )

        # 상태 코드 확인
        if response.status_code == 200:
            # 세션 완전히 삭제
            st.session_state.clear()
            st.success("✅ 로그아웃 되었습니다.")
            # 처음 화면으로 돌아감
            st.rerun()  # UI 갱신
        else:
            st.error("🚨 로그아웃 실패!")
    # 세션 만료 시
    else:
        st.warning("🚨 로그인 상태가 아닙니다.")


# 🔹 사이드바 메뉴
# 로그인 상태 시
if "auth_token" in st.session_state:
    # username 출력
    st.sidebar.write(f"✅ 로그인됨: {st.session_state['username']}")
    # 로그아웃 버튼을 누르면 로그아웃 실행
    if st.sidebar.button("로그아웃"):
        logout()
    # 사이드바에 챗봇, 개인 페이지 옵션 설정
    menu = st.sidebar.selectbox("메뉴 선택", ["챗봇", "MyPage"])
else:
    # 로그인과 회원가입 옵션 설정
    menu = st.sidebar.selectbox("메뉴 선택", ["로그인", "회원가입"])


# 개인 페이지에서 유저 정보를 불러올 함수 설정
def get_user_info():
    """유저 정보를 가져오는 함수"""
    # 로그인 상태에서 진행하기에 access token 가져오기
    headers = {"Authorization": f"Bearer {st.session_state.get('auth_token', '')}"}
    # DRF 프로필 API에 요청
    response = requests.get(f"{BASE_URL}/account/profile/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# 유저의 선호 장르 불러오기 (아직 미구현 ❌)
def update_user_genre(selected_genres):
    """유저의 선호 장르를 업데이트하는 함수"""
    headers = {"Authorization": f"Bearer {st.session_state.get('auth_token', '')}"}
    
    user_info = get_user_info()
    existing_otts = user_info.get("subscribed_ott", [])  # 기존 구독 OTT 유지

    # 기존 OTT 정보를 유지하면서 장르만 업데이트
    data = {
        "preferred_genre": selected_genres,
        "subscribed_ott": existing_otts  # ✅ 기존 OTT 값 유지
    }
    response = requests.put(f"{BASE_URL}/account/profile/", json=data, headers=headers)

    return response.status_code == 200  # 성공 여부 반환

# 유저의 구독중인 ott 불러오기
def update_user_ott(selected_otts):
    """유저의 선호 장르를 업데이트하는 함수"""
    headers = {"Authorization": f"Bearer {st.session_state.get('auth_token', '')}"}
    user_info = get_user_info()
    existing_genres = user_info.get("preferred_genre", [])  # 기존 선호 장르 유지

    # 기존 장르 정보를 유지하면서 OTT만 업데이트
    data = {
        "preferred_genre": existing_genres,  # ✅ 기존 선호 장르 값 유지
        "subscribed_ott": selected_otts
    }
    response = requests.put(f"{BASE_URL}/account/profile/", json=data, headers=headers)
    
    
    return response.status_code == 200  # 성공 여부 반환

# 개인 페이지 불러오기
def myPage():
    # 현재 페이지명 명시
    st.subheader("👤 마이페이지 (My Page)")

    # 🔹 유저 정보 불러오기
    user_info = get_user_info()
    # 세션에 유저 정보 저장
    st.session_state["user_info"] = user_info

    if user_info:
        # 이메일 명시
        st.write(f"**📧 이메일:** {user_info['email']}")

        # 현재 선호 장르 표시
        current_genre = user_info.get("preferred_genre", "설정되지 않음")
        st.write(f"🎭 현재 선호 장르: `{current_genre}`")

        # 🔹 장르 선택 (드롭다운)
        genre_list = [
            "Action",
            "Adventure",
            "Animation",
            "Comedy",
            "Crime",
            "Documentary",
            "Drama",
            "Family",
            "Fantasy",
            "History",
            "Horror",
            "Music",
            "Mystery",
            "Romance",
            "Science Fiction",
            "Thriller",
            "War",
            "Western",
        ]

        selected_genres = st.multiselect(
            "🎬 변경할 선호 장르 선택", genre_list, default=current_genre
        )
        
        # 🔹 장르 업데이트 버튼 (아직 구현 ❌)
        if st.button("선호 장르 업데이트"):
            if update_user_genre(selected_genres):
                st.success(
                    f"✅ 선호 장르가 `{selected_genres}`(으)로 업데이트되었습니다!"
                )
                st.session_state["user_info"][
                    "preferred_genre"
                ] = selected_genres  # UI 갱신
            else:
                # 현재 Bad Request: /account/profile/ "PUT /account/profile/ HTTP/1.1" 400 72
                st.error("🚨 장르 업데이트 실패!")



        # 현재 구독중인 ott 표시
        current_ott = user_info.get("subscribed_ott", "설정되지 않음")
        st.write(f"🎭 현재 구독중인 ott: `{current_ott}`")
        
        # 🔹 구독 OTT 선택 (드롭다운)
        ott_list = [
            "Netflix",
            "Watcha",
            "Wavve",
            "Tving",
            "Coupang Play",
            "Disney+",
            "Hulu",
            "Prime Video",
        ]
        selected_otts = st.multiselect(
            "🎬 변경할 구독 OTT 선택", ott_list
        )

            
        if st.button("구독중인 ott 업데이트"):
            if update_user_ott(selected_otts):
                st.success(
                    f"✅ 구독중인 ott가 `{selected_otts}`(으)로 업데이트되었습니다!"
                )
                st.session_state["user_info"][
                    "subscribed_ott"
                ] = selected_otts  # UI 갱신
            else:
                # 현재 Bad Request: /account/profile/ "PUT /account/profile/ HTTP/1.1" 400 72
                st.error("🚨 구독중인 ott 업데이트 실패!")

    else:
        st.error("🚨 유저 정보를 불러오지 못했습니다.")


# 🔹 메뉴 이동 (로그인 상태에 따라 로그인/회원가입 숨김)
# 로그인 전에 메뉴가 '로그인'인 경우
if menu == "로그인" and "auth_token" not in st.session_state:
    login()
# 로그인 전 메뉴가 '회원가입'일 경우
elif menu == "회원가입" and "auth_token" not in st.session_state:
    signup()
# 로그인 후 메뉴가 'MyPage'인 경우
elif menu == "MyPage" and "auth_token" in st.session_state:
    myPage()

# ✅ 챗봇 UI
if "auth_token" in st.session_state and menu == "챗봇":
    st.subheader("💬 AI 챗봇")
    
    # 사용자가 선택할 수 있는 언어 설정
    language_options = {"한국어": "ko", "English": "en", "日本語": "ja"}
    selected_language = st.sidebar.selectbox("🌍 언어 선택 (Language)", list(language_options.keys()), index=0)  

    # 선택한 언어를 세션에 저장
    st.session_state["language"] = language_options[selected_language]  
    
    
    # 기존 메시지 출력 / 세션의 저장된 메세지를 차례대로 출력
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
        headers = {
            "Authorization": f"Bearer {st.session_state.get('auth_token', '')}"
        }  # 🔥 JWT 토큰 추가
        response = requests.post(
            API_URL,
            json={"question": user_input, "language": st.session_state["language"]}, headers=headers
        )

        bot_reply = (
            response.json()["answer"]
            if response.status_code == 200
            else "오류 발생: API 요청 실패"
        )

        # 챗봇 응답 추가
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
