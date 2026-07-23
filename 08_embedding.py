from langchain_huggingface import HuggingFaceEmbeddings


def str_embedding():
    embedding = HuggingFaceEmbeddings(
        model_name="/data/models/embedding/bge-base-zh-v1.5",
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )

    query_str = "我是大帅哥！"

    query_embedding = embedding.embed_query(query_str)

    print("向量维度：", len(query_embedding))
    print("前 10 个数值：", query_embedding[:10])

    query_list = ["北京", "上海", "广州"]

    res = embedding.embed_documents(query_list)

    print(res)

if __name__ == "__main__":
    str_embedding()