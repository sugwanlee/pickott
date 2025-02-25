from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings

# Data Load
loader = CSVLoader(
    file_path="./data/tmdb_data.csv",
    encoding="utf-8",
)
whole_data = loader.load()
# print(whole_data)

# Splitter 제거: 한 행씩 벡터로 저장하므로 텍스트 스플리터가 필요 없습니다.
# splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# split_data = splitter.split_documents(whole_data)

# Embedding

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    )


# Vector Store
vector_store = Chroma.from_documents(
    documents=whole_data, # split_data 대신 whole_data 를 그대로 사용
    embedding=embeddings,
    persist_directory="my_vector_store",
)