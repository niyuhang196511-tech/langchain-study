from FlagEmbedding import BGEM3FlagModel

def vector():
    model = BGEM3FlagModel(
        model_name_or_path="/data/models/embedding/bge-m3",
        # 返回稠密向量
        return_dense=True,
        # 返回稀疏向量
        return_sparse=True
    )

    res = model.encode("你好，我是大帅哥！")


    print(res)

    # 稠密向量
    dense_vector = res['dense_vecs']

    # 稀疏向量
    sparse_vector = res['lexical_weights']

    print(dense_vector)
    print(sparse_vector)

    sparse_vector_to_id = model.convert_id_to_token(sparse_vector)
    print(sparse_vector_to_id)

if __name__ == '__main__':
    vector()