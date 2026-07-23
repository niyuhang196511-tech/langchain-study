from pymilvus import MilvusClient, DataType

# 创建客户端
client = MilvusClient(
    uri="http://localhost:19530",
    # token="root:Milvus"
)


# 创建 schema
def create_schema():
    schema = MilvusClient.create_schema(
        # 自增ID
        auto_id=True,
    )

    # 添加字段
    # 主键
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    # 稠密向量
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
    # 块信息
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=10000)
    # 元数据
    schema.add_field(field_name="metadata", datatype=DataType.JSON)
    # 稀疏向量
    schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)

    return schema


# 创建索引
def create_index():
    # 创建索引
    index_params = MilvusClient.prepare_index_params()

    index_params.add_index(field_name="vector", index_type="HNSW", metric_type="L2")
    index_params.add_index(field_name="sparse_vector", index_type="SPARSE_INVERTED_INDEX", metric_type="IP")

    return index_params


# 创建collection
def create_collection():
    client.create_collection(
        collection_name="test",
        schema=create_schema(),
        index_params=create_index()
    )

if __name__ == '__main__':
    create_collection()

    print(client.list_collections())

    print(client.describe_collection("test"))