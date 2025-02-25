# 사용자 맞춤 영화 추천 AI 챗봇 

<br><br>

## 피콧 (PIck Ott)

![프로젝트 대표 이미지](https://github.com/user-attachments/assets/fd368a46-6b62-4f41-b01f-e42d33f024a9)



<br>


**피콧**은 Django 기반의 웹 서비스로, LangChain과 RAG를 활용하여 영화 관련 정보를 제공하는 영화 추천 챗봇입니다. <br>
사용자의 관심사(최신 영화, OTT 별 영화, 장르별 영화)와 대화 기록을 반영하여 맞춤형 영화 추천을 제공합니다.



<br><br>

## 💡 프로젝트 핵심 목표

1. 최신 영화 추천 정확도 향상
   - LangChain + RAG 기반 검색을 활용해 최신 영화에 대한 정보를 반영

2. 사용자가 선택한 선호 장르와 사용 OTT 기반 영화 추천
   * my page에 작성된 사용자별 선호 장르와 OTT 구독 정보를 반영해 개인 맞춤형 추천 시스템 구축

3. 사용자(회원)별 대화 기록을 저장 및 갱신해 기존 대화 맥락 유지
   * LangChain의 메모리 기능을 활용해 이전 대화를 기반으로 답변 생성


<br><br>


### 🍁 사용자의 구독 정보를 바탕으로 선호하는 장르 영화 추천

---

1. **한 줄 요약**  
    - RAG를 사용하여 최신 영화 정보와 OTT 서비스 플랫폼 정보를 이용
    - LLM을 사용하여 사용자 데이터와 RAG를 취합하여 향상된 추천 서비스 제공



2. **도입 배경**  
	- 기존 추천 서비스는 각 OTT 내에서만 추천할 뿐이며, 추천 이유를 제시하지 않음

     
3. **기술적 선택지** 

	1. LLM 기반 추천
		- 사전 학습된 데이터를 기반으로 추천을 수행하여 최신 영화 정보를 반영하지 못함
		- 영어와 한국어와 같이 질문 입력 방식에 따라 모델의 답변이 달라짐

	2. <u>**LLM + RAG 기반 추천**</u>
		- 추천 모델에 RAG를 추가하여 최신 정보 검색 가능
		- RAG 실행 전에 LLM으로 사용자 입력을 정제한 후 검색을 수행해 답변 정확도 향상
	 
        `결론`: LangChain과 RAG를 통해 최신 정보를 반영하고 정보 검색 정확도를 향상, 좀 더 사용자에게 맞는 추천 제공

<br><br>

## 🍁 트러블 슈팅


1. **배경**
   - **영화 제목 검색을 한글이 아닌 영어로만 인식**  
     - 제목 검색을 영어로만 인식,최신 영화를 불러오지 못 함.

   - **rag를 사용할 때 리트리버가 데이터를 제대로 가져오지 않음**  
     - 챗봇이 답변에 알맞은 영화 정보를 알려주지 않음 

2. **문제**  
   - **날짜, 및 번역하지 않은 언어 프롬프팅 문제**
     - 벡터DB에서 정보를 가져올 때 한글로 인풋을 넣는게 문제

3. **해결 방안**  
     - 날짜가 23년도에 머물러 있어, 프롬프트에 날짜를 추가
    ![Image](https://github.com/user-attachments/assets/0013aacb-d5cf-4527-ba4b-ca12e20a762d)
     - 벡터DB를 거치기 전(리트리버 사용 전) 컴포넌트를 추가 해 기본 llm을 이용 해 영어로 번역 후 리트리버 사용
    ![Image](https://github.com/user-attachments/assets/0bfa1367-0cbb-4a68-a8ab-a56b3bcbf420)  



<br><br>


## 인프라 아키텍처 & 적용 기술

### 아키텍처 다이어그램
![Image](https://github.com/user-attachments/assets/595612bf-9a44-4cac-b58f-5837516bdfc0)

- Django 기반의 웹 서비스를 이용하여 영화 관련 정보, 회원의 대화 기록 바탕으로 맞춤형 영화 추천을 제공합니다.
- 이용자의 사용 언어를 고려해 다국어 지원을 하고 있습니다.


---

<details>
<summary><b>📦 적용 기술 상세보기</b></summary>

### 💾 **백엔드**
1. **Django REST framework**  
   - **적용 위치**: 메인 서버  
   - **사용 이유**: 강력하고 유연하게 RESTful api를 쉽게 구현할 수 있으며, JWT, Session 등 다양한 인증 방식 및 기능을 제공하기 때문에 프로젝트 규모 및 주제에 적합
2. **JWT**
   - **적용 위치**: 메인 서버
   - **사용 이유**: 세션/쿠키 방식보다 확장성이 뛰어남, 안전한 토큰 기반 인증
3. **ChromaDB**
   - **적용 위치**: 메인 서버
   - **사용 이유**: 가장 많이 사용하는 벡터db, 경량화 되어 있고, 작은 프로젝트에 적합
4. **langchain**
   - **적용 위치**: 메인 서버
   - **사용 이유**: LLM을 확장하기 위한 기능들을 쉽게 연동 할 수 있고, 체인(Chain) 기반 워크플로우 구축 가능, 메모리 기능 지원
---

### 🌐 **프론트앤드**
1. **스트림릿**  
   - **적용 위치**: 웹
   - **사용 이유**: 데이터 시각화, 데이터 탐색, 모델 적용이 쉽고 간편하게 개발 용이


</details>

<br><br>

## 주요 기능


### 🍁 회원 기능
   - 선호 장르 선택:
      - 사용자가 선호하는 복수 장르 선택
      - Many to Many 필드를 사용해 복수 장르 선택 적용
   - 구독한 OTT 정보 입력: 
      - 사용자가 구독한 OTT 정보 복수 선택
      - Many to Many 필드를 사용해 OTT 정보 복수 선택 적용



### 🍁 챗봇 기능
   - 사용자가 선호하는 장르 및 OTT 기반 영화 추천
      - 회원 정보를 반영한 사용자 맞춤형 영화 추천 챗봇
   - 최신 영화 추천
      - LangChain + RAG 기반 검색을 활용해 최신 영화에 대한 정보를 반영
   - 기존 대화 맥락 유지
      - RDB + 메모리 기반 세션을 이용하여 기존 대화 내역을 반영
   - 다국어 기능 구현
      - 프롬프팅 기법을 이용해 언어별 답변 제공


---

