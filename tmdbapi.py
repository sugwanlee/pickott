import requests
import json
import os

# ✅ API 키 설정 (발급받은 키로 변경해야 함)
API_KEY = os.environ.get("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/movie/popular"
LANGUAGE = "ko-KR"
TOTAL_MOVIES = 1000  # 가져올 영화 개수
MOVIES_PER_PAGE = 20  # TMDB 기본 한 페이지당 영화 수
TOTAL_PAGES = TOTAL_MOVIES // MOVIES_PER_PAGE  # 필요한 페이지 수

# ✅ 영화 데이터를 저장할 리스트
all_movies = []

# ✅ 여러 페이지에서 영화 데이터를 가져오기
for page in range(1, TOTAL_PAGES + 1):
    url = f"{BASE_URL}?api_key={API_KEY}&language={LANGUAGE}&page={page}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        all_movies.extend(data["results"])  # 영화 리스트 추가
    else:
        print(f"Error: {response.status_code}")
        break  # API 요청 실패 시 중단

# ✅ JSON 파일로 저장 (선택 사항)
with open("tmdb_movies.json", "w", encoding="utf-8") as f:
    json.dump(all_movies, f, indent=4, ensure_ascii=False)

print(f"총 {len(all_movies)}개의 영화 데이터를 가져왔습니다!")