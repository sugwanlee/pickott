import requests
import pandas as pd
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

# ✅ API 설정 (동일)
API_KEY = "c234b78378505e7923239242c0ae8fde" # 실제 API 키로 변경 필요!
BASE_URL = "https://api.themoviedb.org/3/discover/movie"
WATCH_PROVIDERS_URL = "https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
GENRE_URL = "https://api.themoviedb.org/3/genre/movie/list"
LANGUAGE = "ko-KR"
MOVIES_PER_PAGE = 20

# ✅ 날짜 범위 설정 (동일)
start_date = date(2023, 10, 1)
end_date = date(2025, 2, 21)
date_format = "%Y-%m-%d"

# ✅ 요청 세션 생성 (동일)
session = requests.Session()

def get_genre_map():
    """장르 ID → 장르명 매핑 가져오기 (동일)"""
    response = session.get(GENRE_URL, params={"api_key": API_KEY, "language": LANGUAGE})
    if response.status_code == 200:
        return {genre["id"]: genre["name"] for genre in response.json().get("genres", [])}
    print(f"⚠️ 장르 정보를 가져오지 못했습니다. (Error: {response.status_code})")
    return {}

def fetch_movie_data(page, start_date_str, end_date_str):
    """특정 페이지, 특정 기간, 한국 개봉 영화 데이터 가져오기 (동일)"""
    params = {
        "api_key": API_KEY,
        "language": LANGUAGE,
        "page": page,
        "primary_release_date.gte": start_date_str,
        "primary_release_date.lte": end_date_str,
        "region": "KR",
        "sort_by": "popularity.desc"
    }
    response = session.get(BASE_URL, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        return results if results else []
    print(f"Error: {response.status_code} on page {page}")
    return []

def fetch_watch_providers(movie_id):
    """특정 영화의 OTT 제공 서비스 가져오기 (동일)"""
    response = session.get(
        WATCH_PROVIDERS_URL.format(movie_id=movie_id), params={"api_key": API_KEY}
    )
    if response.status_code == 200:
        watch_data = (
            response.json().get("results", {}).get("KR", {}).get("flatrate", [])
        )
        return ", ".join(provider["provider_name"] for provider in watch_data) if watch_data else ""
    return ""

def process_movie(movie, genre_map):
    """영화 데이터 처리 및 변환 (OTT 플랫폼 정보 유지, 변경 없음)"""
    return {
        "type": "movie",
        "original_title": movie["original_title"],
        "title": movie["title"],
        "overview": movie["overview"],
        "release_date": movie["release_date"],
        "popularity": movie["popularity"],
        "vote_average": movie["vote_average"],
        "genres": ", ".join([genre_map.get(genre_id, "기타") for genre_id in movie["genre_ids"]]),
        "ott_platforms": None, # 초기화, ThreadPoolExecutor 에서 채워넣을 예정
    }


# ✅ 장르 매핑 가져오기 (동일)
genre_map = get_genre_map()

# ✅ 영화 데이터 가져오기 및 처리 (병렬 처리, OTT 플랫폼 정보 유지)
movies_data = []
start_date_str = start_date.strftime(date_format)
end_date_str = end_date.strftime(date_format)
current_page = 1

with ThreadPoolExecutor(max_workers=5) as executor:
    while True:
        movies = fetch_movie_data(current_page, start_date_str, end_date_str)
        if not movies:
            print(f"페이지 {current_page}에서 영화 데이터가 없습니다. 데이터 수집 완료.")
            break

        # 영화 데이터 processing 작업과 OTT 플랫폼 정보 fetching 작업을 병렬로 실행
        futures = []
        for movie in movies:
            processed_movie = process_movie(movie, genre_map) # process_movie 먼저 호출
            future_ott = executor.submit(fetch_watch_providers, movie['id']) # OTT fetching 작업 submit
            futures.append((processed_movie, future_ott)) # processed_movie 와 future_ott 를 묶어서 저장

        for processed_movie, future_ott in futures: # as_completed 대신 futures 리스트 순회
            processed_movie['ott_platforms'] = future_ott.result() # future.result() 로 OTT 플랫폼 정보 가져와서 채우기
            movies_data.append(processed_movie)

        print(f"페이지 {current_page} 데이터 수집 완료. 현재 누적 영화 수: {len(movies_data)}")
        current_page += 1
        time.sleep(0.5)


# ✅ CSV 저장 (동일)
df = pd.DataFrame(movies_data)
df.to_csv("tmdb_movies_kr_release_efficient_ott.csv", index=False, encoding="utf-8") # 파일명 변경
print(f"총 {len(movies_data)}개의 영화 데이터를 CSV 파일 (tmdb_movies_kr_release_efficient_ott.csv) 로 저장했습니다!")
