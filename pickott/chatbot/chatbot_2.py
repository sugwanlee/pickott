from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from pathlib import Path
from dotenv import load_dotenv
import datetime
import os
import pandas as pd

today = datetime.datetime.today().strftime(
    "%D"
)  # 오늘 날짜를 'MM/DD/YY' 형식의 문자열로 저장합니다.


# .env 파일 경로 설정 및 로드
BASE_DIR = Path(__file__).resolve().parents[2] # 파일 경로 설정
load_dotenv(BASE_DIR / '.env') # 환경 변수 로드

# API 키 확인을 위한 디버깅 출력
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}") # 디버깅 출력 : 정상 작동하면 Yes

# ChatOpenAI 초기화
chat = ChatOpenAI(model="gpt-4o", api_key=api_key)

chat_history = ChatMessageHistory()

StrOutputParser = StrOutputParser()


def summarize_messages(chain_input):
    stored_messages = chat_history.messages
    if len(stored_messages) == 0:
        return False
    summarization_prompt = ChatPromptTemplate.from_messages(
        [
            ("placeholder", "{chat_history}"),
            (
                "user",
                "Distill the above chat messages into a single summary message. Include as many specific details as you can.",
            ),
        ]
    )
    summarization_chain = summarization_prompt | chat

    # chat_history 에 저장된 대화 기록을 요약프롬프트에 입력 & 결과 저장
    summary_message = summarization_chain.invoke({"chat_history": stored_messages})
    # chat_history 에 저장되어있던 기록 지우기

    # print(id(chat_history))
    # chat_history.clear()
    # print(id(chat_history))
    # 생성된 새로운 요약내용으로 기록 채우기
    chat_history.add_message(("assistant", summary_message.content))
    # print(summary_message.content)

    return True


def chatbot_call(user_input, user):
    # 유저의 선호 장르 가져오기
    user_genres = [genre.name for genre in user.preferred_genre.all()]
    

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a movie recommendation assistant. Your goal is to provide helpful and relevant movie recommendations. YOU MUST ANSWER IN KOREAN.
                    - today is {today}
                     - user's preferred genres: {user_genres} 
                - Please consider user's preferred genres when recommending movies
                """, # {user_genres} 추가
            ),
            ("system", "{context}"),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | chat | StrOutputParser

    chain_with_message_history = RunnableWithMessageHistory(
        chain,  # 실행할 Runnable 객체
        lambda session_id: chat_history,  # 세션 기록을 가져오는 함수
        input_messages_key="input",  # 입력 메시지의 Key
        history_messages_key="chat_history",  # 대화 히스토리 메시지의 Key
    )

    chain_with_summarization = (
        RunnablePassthrough.assign(messages_summarized=summarize_messages)
        | chain_with_message_history
    )
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(
        persist_directory=f"{BASE_DIR}/my_vector_store", embedding_function=embeddings
    )

# 수정 전 ───────────────────────────────────────────────────────────────────────────
    # # 벡터 DB가 비어 있는지 체크
    # if not vector_store._collection.count():
    #     print("기존 벡터 DB에 데이터가 없습니다. 먼저 임베딩을 수행하세요.")
    # else:
    #     print("기존 벡터 DB를 불러왔습니다.")



# 수정 된 코드

    # 벡터 DB가 비어 있는지 체크
    if not vector_store._collection.count():
        print("기존 벡터 DB에 데이터가 없습니다. 임베딩을 수행합니다...")
        # CSV 파일에서 데이터 읽기
        df = pd.read_csv(f"{BASE_DIR}/data/tmdb_movies_5000.csv")
        
        # 임베딩할 텍스트 준비
        texts = df.apply(
            lambda x: f"Title: {x['title']}\nOriginal Title: {x['original_title']}\n"
                    f"Genre: {x['genres']}\nOverview: {x['overview']}\n"
                    f"Release Date: {x['release_date']}", 
            axis=1
        ).tolist()
        
        # 데이터 임베딩
        vector_store.add_texts(texts)
        # vector_store.persist()  # 최신 버전의 Chroma에서는 persist() 메서드가 필요 없다고 함.
        print(f"임베딩 완료: {len(texts)}개의 영화 데이터가 저장되었습니다.")
    else:
        print("기존 벡터 DB를 불러왔습니다.")

#까지 수정 후 ───────────────────────────────────────────────────────────────────────────



    # 벡터DB에서 질문을 검색할 리트리버
    retriever = vector_store.as_retriever()

    docs = retriever.invoke(user_input)
    context = "\n".join([doc.page_content for doc in docs])

    answer = chain_with_summarization.invoke(
        {
            "input": user_input,
            "context": context,
            "today": today,
            "user_genres": ", ".join(user_genres), # 유저의 선호 장르 추가
        },
        {"configurable": {"session_id": user}},
    )
    return answer
