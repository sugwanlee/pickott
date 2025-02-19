from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
import os
import datetime

LANGSMITH_TRACING = True
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = "pr-upbeat-almond-24"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
today = datetime.datetime.today().strftime(
    "%D"
)  # 오늘 날짜를 'MM/DD/YY' 형식의 문자열로 저장합니다.


# 정상화
def chat_call(user_input):
    # 기존 임베딩된 데이터 활용
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(
        persist_directory="C:/Users/LEE/Documents/github_repo/chtbot_pjt/my_vector_store",
        embedding_function=embeddings,
    )

    # 벡터 DB가 비어 있는지 체크
    if not vector_store._collection.count():
        print("기존 벡터 DB에 데이터가 없습니다. 먼저 임베딩을 수행하세요.")
    else:
        print("기존 벡터 DB를 불러왔습니다.")
        print(vector_store._collection.count())

    # 벡터DB에서 질문을 검색할 리트리버
    retriever = vector_store.as_retriever()
    #
    prompt = ChatPromptTemplate.from_template(
        """
        You are a movie recommendation assistant. Your goal is to provide helpful and relevant movie recommendations.

        - today is {today}
        - If the question is in Korean, search for both the Korean and original titles.
        - Recommend movies across different streaming platforms if possible.
        - If a specific movie is mentioned, provide key details (title, genre, release year, director, and a short plot summary).
        - If the movie is unavailable in the database, suggest similar movies instead of saying "not available."
        - Keep the answer concise but informative.

        Context: {context}
        Question: {question}
        Answer:
        """
    )

    # 사용자 입력 받기
    question = user_input

    # 벡터 DB에서 관련 문서 검색
    docs = retriever.invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    print("------" * 10)
    print(context)

    # LLM 설정
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv(OPENAI_API_KEY))

    # RAG 실행
    chain = prompt | llm
    res = chain.invoke({"context": context, "question": question, "today": today})

    return res.content
