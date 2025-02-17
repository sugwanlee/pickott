from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory

# 정상화
def chat_call(user_input):
    # 기존 임베딩된 데이터 활용
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma( 
        persist_directory="C:/Users/LEE/Documents/github_repo/chtbot_pjt/my_vector_store", embedding_function=embeddings)

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
    당신은 영화 추천 전문 봇입니다.
    검색된 다음 문맥을 사용하여 질문에 답하세요.
    ott별로 최소 1개씩 추천해주세요.
    없으면 없다고 알려주세요.
    
    Question: {question}
    Context: {context}
    Answer: """
    )

    # 사용자 입력 받기
    question = user_input

    # 벡터 DB에서 관련 문서 검색
    docs = retriever.invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    print(context)

    # LLM 설정
    llm = ChatOpenAI(model="gpt-4o")

    # RAG 실행
    chain = prompt | llm
    res = chain.invoke({"context": context, "question": question})

    return res.content