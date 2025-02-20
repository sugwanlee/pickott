from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
import os
import datetime
from pathlib import Path

today = datetime.datetime.today().strftime("%D")  # 오늘 날짜를 'MM/DD/YY' 형식의 문자열로 저장합니다.

api_key = os.getenv("OPENAI_API_KEY")

chat = ChatOpenAI(model="gpt-4o", api_key=api_key)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a movie recommendation assistant. Your goal is to provide helpful and relevant movie recommendations. YOU MUST ANSWER IN KOREAN.
                - today is {today}
            """,
        ),
        ("system", "{context}"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)
StrOutputParser = StrOutputParser()
chain = prompt | chat | StrOutputParser

chat_history = ChatMessageHistory()


chain_with_message_history = RunnableWithMessageHistory(
    chain, # 실행할 Runnable 객체
    lambda session_id: chat_history, # 세션 기록을 가져오는 함수
    input_messages_key="input", # 입력 메시지의 Key
    history_messages_key="chat_history", # 대화 히스토리 메시지의 Key
)




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

chain_with_summarization = (
    RunnablePassthrough.assign(messages_summarized=summarize_messages)
    | chain_with_message_history
)

while True:
    user_input = input()
    if user_input in ["그만", "끝"]:
        break
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma( 
        persist_directory="../../my_vector_store"

    # 벡터 DB가 비어 있는지 체크
    if not vector_store._collection.count():
        print("기존 벡터 DB에 데이터가 없습니다. 먼저 임베딩을 수행하세요.")
    else:
        print("기존 벡터 DB를 불러왔습니다.")

    # 벡터DB에서 질문을 검색할 리트리버
    retriever = vector_store.as_retriever()

    docs = retriever.invoke(user_input)
    context = "\n".join([doc.page_content for doc in docs])
    
    answer = chain_with_summarization.invoke(
        {"input": user_input, "context" : context, "today" : today},
        {"configurable": {"session_id": "unused"}},
    )
    # chat_history.add_message(("human", user_input))
    # chat_history.add_message(("assistant", answer))
    print(answer)
    print("-------"*15)