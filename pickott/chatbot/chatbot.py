# from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pathlib import Path
import datetime
import os
from account.models import User


BASE_DIR = Path(__file__).resolve().parents[2]
# API키 환경변수에서 가져오기
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

# 오늘 날자를 변수에 담기기
today = datetime.datetime.today().strftime("%D")

# 챗봇 모델 설정
chat = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# 파서
str_outputparser = StrOutputParser()

# 템플릿
prompt = ChatPromptTemplate.from_messages(
    [   MessagesPlaceholder(variable_name="chat_history"),
        # - 스트리밍 플랫폼(넷플릭스, 디즈니+, 왓챠 등)에서 볼 수 있는 영화를 각 플랫폼마다 하나씩 추천하세요.
        (
            "system",
            """당신은 영화 추천 전문가입니다. 반드시 다음 언어로 답변하시오 : {language}.
                - 아래의 조건을 기반으로 추천하세요.
                - 오늘은 {today}입니다. 오늘자 이전의 영화를 알려주세요.
                - {genre}는 유저가 선호하는 장르입니다. 장르를 고려해서 평점이 높은 영화를 추천해주세요.
                - {ott}각 ott별로 하나씩 추천하고, 없으면 ott 구분하지 말고 추천해주세요.
                - 각 영화마다 간략한 줄거리, 개봉일, 평점, 추천 이유, 그리고 해당 ott에서 볼 수 있는지 여부를 명확히 제시하세요.
                - "최신", "최근", "요새" 라는 키워드가 질문에 있을때만 다음 영화들에서 추천하십시오 : {context}
            """,
        ),
        # 물어본 질문(user_input)
        ("human", "{input}"),
    ]
)

store = {}

if User.objects.exists():
    for u in User.objects.all():
        store[u.username] = ChatMessageHistory()
        if u.chatbots is not None:
            for c in u.chatbots.order_by('-pk')[:5]:
                store[u.username].add_message(HumanMessage(content=c.question))
                store[u.username].add_message(AIMessage(content=c.answer))

# 임베딩 모델 설정
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    )

# 벡터db 설정
vector_store = Chroma( 
    persist_directory= f"{BASE_DIR}/my_vector_store", embedding_function=embeddings)


# 벡터 DB가 비어 있는지 체크
if not vector_store._collection.count():
    print("기존 벡터 DB에 데이터가 없습니다. 먼저 임베딩을 수행하세요.")
else:
    print("기존 벡터 DB를 불러왔습니다.")

# 벡터DB에서 질문을 검색할 리트리버
retriever = vector_store.as_retriever()


def docs_join_logic(docs):
    return "\n".join([doc.page_content for doc in docs])
# 가져온 문서 붙이기

docs_join = RunnableLambda(docs_join_logic)

# 체인
rag_chain = chat | str_outputparser | retriever | docs_join
chain = prompt | chat | str_outputparser


# 대화 세션에 대화를 입력해줄 함수
def get_session_history(session_ids):
    if session_ids not in store:  # 세션 ID가 store에 없는 경우
        # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
        store[session_ids] = ChatMessageHistory()
    return store[session_ids]  # 해당 세션 ID에 대한 세션 기록 반환



# 체인을 묶어 기억해줄 객체
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,  # 세션을 기록하는 함수
    input_messages_key="input",  # 사용자의 질문이 템플릿 변수에 들어갈 key
    history_messages_key="chat_history",  # 기록 메시지의 키
)


def chatbot_call(user_input, username, genre, ott, language):

    context = rag_chain.invoke(f"Translate the following question into English: {user_input}, {ott}, {genre}")
    answer = chain_with_history.invoke(
        {"language" : language, "today" : today, "genre" : genre, "ott" : ott, "input" : user_input, "context" : context},
        config={"configurable": {"session_id": username}}
    )
    return answer