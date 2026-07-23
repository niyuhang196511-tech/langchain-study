from langchain_community.document_loaders import UnstructuredMarkdownLoader
from pymilvus import MilvusClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from FlagEmbedding import BGEM3FlagModel
import numpy as np

client = MilvusClient()

def insert_data():
    # 加载文件
    docs = UnstructuredMarkdownLoader("./assets/simple.md").load()

    # 文档切块
    chunks = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=100,
        chunk_overlap=20,
        add_start_index=True
    ).split_documents(docs)

    model = BGEM3FlagModel(
        model_name_or_path="/data/models/embedding/bge-m3",
        return_dense=True,
        return_sparse=True,
    )

    res = model.encode([chunk.page_content for chunk in chunks])

    dense_vector = np.asarray(res['dense_vecs'], dtype=np.float32)
    sparse_vector = res['lexical_weights']

    insert_data = []

    for chunk,dense_vector, sparse_vector in zip(chunks, dense_vector, sparse_vector):
        insert_data.append({
            "vector": dense_vector,
            "sparse_vector": sparse_vector,
            "text": chunk.page_content,
            "metadata": chunk.metadata
        })

    client.insert(
        collection_name="test",
        data=insert_data,
    )
if __name__ == '__main__':
    insert_data()