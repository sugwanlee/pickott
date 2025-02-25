import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PickOtt")
language_options = {"Korean": "한국어", "English": "English", "Japanese": "日本語"}
selected_language = st.sidebar.selectbox("🌍 Language", list(language_options.values()), index=0)
st.session_state["language"] = selected_language

# 선택한 언어를 세션에 저장
st.session_state["language"] = selected_language

if st.session_state["language"] == "한국어":
    st.title("🤖 AI 피콧")
elif st.session_state["language"] == "English":
    st.title("🤖 AI PickOtt")
else:
    st.title("🤖 AI ピックオット")

# API 엔드포인트
API_URL = "http://127.0.0.1:8000/chatbot/"

# 세션에 대화 기록 저장 저장
if "messages" not in st.session_state:
    st.session_state.messages = []


# 회원가입
def signup():
    if st.session_state["language"] == "한국어":
        st.subheader("🔑 회원가입")
    elif st.session_state["language"] == "English":
        st.subheader("🔑 Sign Up")
    else:
        st.subheader("🔑 サインアップ")

    # 🔹 세션 상태 초기화 (없을 경우만)
    st.session_state.setdefault("signup_username", "")
    st.session_state.setdefault("signup_password", "")
    st.session_state.setdefault("signup_email", "")

    # 🔹 입력 필드 (세션 상태와 연동)
    username = st.text_input("아이디", key="signup_username")
    password = st.text_input("비밀번호", type="password", key="signup_password")
    email = st.text_input("이메일", key="signup_email")

    if st.button("Sign Up"):
        # DRF 회원 가입 로직에 요청
        signup_response = requests.post(
            f"{BASE_URL}/account/signup/",
            json={"username": username, "password": password, "email": email},
        )

        # 회원가입 후에 자동으로 로그인 진행
        if signup_response.status_code == 201:
            st.success("✅ Congratulations! You have successfully signed up!")

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

                st.success(f"✅ Welcome, {username}!")

                # 🔹 로그인 성공 → 챗봇 화면으로 이동
                st.session_state["menu"] = "PickOtt"
                st.rerun()
            # 로그인 실패 시
            else:
                st.error("🚨 Failed...")
                st.session_state["menu"] = "Login"
                st.rerun()
        # 회원 가입 실패
        else:
            st.error("🚨 Failed... Please try again.")


# 로그인 기능
def login():
    st.subheader("🔐 Login")

    # 필요 데이터 전달
    username = st.text_input("ID", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
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

            st.success("✅ Login successful!")
            # 챗봇 화면으로 전환
            st.rerun()  # UI 갱신
        else:
            st.error("🚨 Failed to login")


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
            st.success("✅ Logout")
            # 처음 화면으로 돌아감
            st.rerun()  # UI 갱신
        else:
            st.error("🚨 Failed")
    # 세션 만료 시
    else:
        st.warning("🚨 You are not logged in.")


# 🔹 사이드바 메뉴
# 로그인 상태 시
if "auth_token" in st.session_state:
    # username 출력
    st.sidebar.write(f"✅ loged in: {st.session_state['username']}")
    # 로그아웃 버튼을 누르면 로그아웃 실행
    if st.sidebar.button("Logout"):
        logout()
    # 사이드바에 챗봇, 개인 페이지 옵션 설정
    menu = st.sidebar.selectbox("Menu", ["PickOtt", "MyPage"])
else:
    # 로그인과 회원가입 옵션 설정
    menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])


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


# 유저의 선호 장르 불러오기
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

    if response.status_code == 200:
        # ✅ 최신 유저 정보 다시 불러오기
        st.session_state["user_info"] = get_user_info()
        st.session_state["genre_update_success"] = f"✅ Preferred genres updated to {selected_genres}!"
        st.rerun()  # 🔥 UI 즉각 반영
    
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
    
    if response.status_code == 200:
        # ✅ 최신 유저 정보 다시 불러오기
        st.session_state["user_info"] = get_user_info()
        st.session_state["ott_update_success"] = f"✅ The otts you are subscribed to have been updated to {selected_otts}!"
        st.rerun()  # 🔥 UI 즉각 반영
    
    return response.status_code == 200  # 성공 여부 반환

# 개인 페이지 불러오기
def myPage():
    # 현재 페이지명 명시
    st.subheader("👤 My Page")

    # 🔹 유저 정보 불러오기
    user_info = get_user_info()
    # 세션에 유저 정보 저장
    st.session_state["user_info"] = user_info

    if user_info:
        # 이메일 명시
        st.write(f"**📧 E-mail:** {user_info['email']}")

        # 현재 선호 장르 표시
        current_genre = user_info.get("preferred_genre", "nothing")
        st.write(f"🎭 Current favorite genre: {current_genre}")
        
        if "genre_update_success" in st.session_state:
            st.success(st.session_state["genre_update_success"])
            del st.session_state["genre_update_success"]

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
            "🎬 Select your preferred genre to change", genre_list, default=current_genre
        )
        
        # 🔹 장르 업데이트 버튼
        if st.button("Update Genre"):
            update_user_genre(selected_genres)
            if not update_user_ott(selected_genres):
                # 현재 Bad Request: /account/profile/ "PUT /account/profile/ HTTP/1.1" 400 72
                st.error("🚨 Update Genre")



        # 현재 구독중인 ott 표시
        current_ott = user_info.get("subscribed_ott", "nothing")
        st.write(f"🎭 Currently subscribed ott: {current_ott}")
        if "ott_update_success" in st.session_state:
            st.success(st.session_state["ott_update_success"])
            del st.session_state["ott_update_success"]
        
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
            "🎬 Select the OTT subscription you want to change", ott_list
        )
        print(selected_otts)

            
        if st.button("Update OTT"):
            update_user_ott(selected_otts)
            if not update_user_ott(selected_otts):
                # 현재 Bad Request: /account/profile/ "PUT /account/profile/ HTTP/1.1" 400 72
                st.error("🚨 Failed update")
        
        
        
        # 1. 회원 탈퇴 상태를 세션에 저장하기 위한 변수 초기화
        # "confirm_withdrawal" 변수는 사용자가 회원 탈퇴 버튼을 클릭한 후 탈퇴 여부를 확인하는 상태를 저장합니다.
        if "confirm_withdrawal" not in st.session_state:
            st.session_state["confirm_withdrawal"] = False

        # 2. 회원 탈퇴 버튼 클릭 또는 이미 탈퇴 확인 상태인 경우 실행
        # st.button("Cancel membership") 버튼을 누르면 True를 반환하지만, 한 번 누른 후에는 False가 되므로 세션 상태를 활용합니다.
        if st.button("Cancel membership") or st.session_state["confirm_withdrawal"]:
            # 사용자가 회원 탈퇴 버튼을 클릭했으므로, 탈퇴 확인 상태를 활성화합니다.
            st.session_state["confirm_withdrawal"] = True
    
            # 탈퇴 확인을 위한 경고 메시지를 출력합니다.
            st.warning("Are you sure you want to withdraw?")
    
            # 3. 탈퇴 확인과 취소를 위한 두 개의 버튼을 나란히 배치하기 위해 컬럼을 생성합니다.
            col1, col2 = st.columns(2)
    
            # 4. 첫 번째 컬럼: "Unsubscribe" 버튼
            if col1.button("Unsubscribe"):
            # API 호출 시 필요한 인증 헤더 설정 (JWT 토큰 사용)
                headers = {
                    "Authorization": f"Bearer {st.session_state.get('auth_token', '')}"
                }
                # 회원 탈퇴 API 엔드포인트에 DELETE 요청 전송
                response = requests.delete(f"{BASE_URL}/account/profile/", headers=headers)
                
                # API 응답이 204 (성공적인 삭제)일 경우
                if response.status_code == 204:
                    st.success("✅ Goodbye!")
                    # 모든 세션 상태를 초기화하여 사용자 정보를 삭제합니다.
                    st.session_state.clear()
                    # UI를 새로고침하여 변경 사항을 즉시 반영합니다.
                    st.rerun()

            # 5. 두 번째 컬럼: "cancel" 버튼
            if col2.button("cancel"):
                st.info("Good choice! 😊")
                # 탈퇴 확인 상태를 False로 변경하여 탈퇴 확인 화면을 닫습니다.
                st.session_state["confirm_withdrawal"] = False

    else:
        st.error("🚨 Fail to take user information...")


# 🔹 메뉴 이동 (로그인 상태에 따라 로그인/회원가입 숨김)
# 로그인 전에 메뉴가 'Login'인 경우
if menu == "Login" and "auth_token" not in st.session_state:
    login()
# 로그인 전 메뉴가 'Sign up'일 경우
elif menu == "Signup" and "auth_token" not in st.session_state:
    signup()
# 로그인 후 메뉴가 'MyPage'인 경우
elif menu == "MyPage" and "auth_token" in st.session_state:
    myPage()

# ✅ 챗봇 UI
if "auth_token" in st.session_state and menu == "PickOtt":

    # 기존 메시지 출력 / 세션의 저장된 메세지를 차례대로 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력
    if user_input := st.chat_input("Ask your question here..."):
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
