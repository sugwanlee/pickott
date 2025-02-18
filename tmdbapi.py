import requests
import pandas as pd
import os
import time
from concurrent.futures import ThreadPoolExecutor

# ✅ API 설정
API_KEY = os.environ.get("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/movie/popular"
WATCH_PROVIDERS_URL = "https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
GENRE_URL = "https://api.themoviedb.org/3/genre/movie/list"
LANGUAGE = "ko-KR"
TOTAL_MOVIES = 5000  # 줄여서 테스트 가능
MOVIES_PER_PAGE = 20
TOTAL_PAGES = TOTAL_MOVIES // MOVIES_PER_PAGE

# ✅ 요청 세션 생성
session = requests.Session()

def get_genre_map():
    """장르 ID → 장르명 매핑 가져오기"""
    response = session.get(GENRE_URL, params={"api_key": API_KEY, "language": LANGUAGE})
    if response.status_code == 200:
        return {genre["id"]: genre["name"] for genre in response.json().get("genres", [])}
    print(f"⚠️ 장르 정보를 가져오지 못했습니다. (Error: {response.status_code})")
    return {}

def fetch_movie_data(page):
    """특정 페이지의 영화 데이터를 가져옴"""
    response = session.get(BASE_URL, params={"api_key": API_KEY, "language": LANGUAGE, "page": page})
    if response.status_code == 200:
        return response.json().get("results", [])
    print(f"Error: {response.status_code} on page {page}")
    return []

def fetch_watch_providers(movie_id):
    """특정 영화의 OTT 제공 서비스 가져오기"""
    response = session.get(WATCH_PROVIDERS_URL.format(movie_id=movie_id), params={"api_key": API_KEY})
    if response.status_code == 200:
        watch_data = response.json().get("results", {}).get("KR", {}).get("flatrate", [])
        return ", ".join(provider["provider_name"] for provider in watch_data) if watch_data else ""
    return ""

def process_movie(movie, genre_map):
    """영화 데이터 처리 및 변환"""
    return {
        "type": "movie",
        "original_title": movie["original_title"],
        "title": movie["title"],
        "overview": movie["overview"],
        "release_date": movie["release_date"],
        "popularity": movie["popularity"],
        "vote_average": movie["vote_average"],
        "genres": ", ".join([genre_map.get(genre_id, "기타") for genre_id in movie["genre_ids"]]),
        "ott_platforms": fetch_watch_providers(movie["id"])
    }

# ✅ 장르 매핑 가져오기
genre_map = get_genre_map()

# ✅ 영화 데이터 가져오기 (병렬 처리)
movies_data = []
with ThreadPoolExecutor(max_workers=5) as executor:
    for page in range(1, TOTAL_PAGES + 1):
        movies = fetch_movie_data(page)
        results = executor.map(lambda m: process_movie(m, genre_map), movies)
        movies_data.extend(results)
        time.sleep(0.5)  # 속도 제한 방지

# ✅ CSV 저장
df = pd.DataFrame(movies_data)
df.to_csv("tmdb_movies.csv", index=False, encoding="utf-8")
print(f"총 {len(movies_data)}개의 영화 데이터를 CSV 파일로 저장했습니다!")
