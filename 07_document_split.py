from langchain_community.document_loaders import UnstructuredWordDocumentLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def document_split():
    file_load = UnstructuredMarkdownLoader("assets/simple.md")
    docs = file_load.load()

    splitter = RecursiveCharacterTextSplitter(
        # 设置切割符
        separators=["\n\n", "\n", " ", ""],
        # 设置块的大小
        chunk_size=100,
        # 设置块重叠的大小
        chunk_overlap=20,
        # 是否添加块的其实索引
        add_start_index=True
    )

    chunks = splitter.split_documents(docs)
    for index, chunk in enumerate(chunks):
        print(f"但前是『{index}』：{chunk}")
        print("==========================")

if __name__ == '__main__':
    document_split()