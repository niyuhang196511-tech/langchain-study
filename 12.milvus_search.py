from FlagEmbedding import BGEM3FlagModel
from pymilvus import MilvusClient
import numpy as np

client = MilvusClient()

def search_by_dense_vector():
    model = BGEM3FlagModel(
        model_name_or_path="/data/models/embedding/bge-m3",
        return_dense=True,
        return_sparse=True,
    )

    search_res = model.encode("LangChain")

    dense_vector = np.asarray(
        search_res["dense_vecs"],
        dtype=np.float32
    )

    search_res = client.search(
        collection_name="test",
        data=[dense_vector],
        anns_field="vector",
        search_params={"metric_type": "L2"},
        output_fields=["id", "text"]
    )
    for hits in search_res:
        for hit in hits:
            print(hit)

if __name__ == '__main__':
    search_by_dense_vector()