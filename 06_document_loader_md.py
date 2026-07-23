from langchain_community.document_loaders import UnstructuredMarkdownLoader

def load_md():

    # # 创建非结构化的MD的加载器
    # file_loader = UnstructuredMarkdownLoader("assets/simple.md")
    #
    # # 一次性加载整合文件
    # docs = file_loader.load()
    #
    # print(docs)

    # 创建非结构化的MD的加载器
    file_loader = UnstructuredMarkdownLoader("assets/simple.md", mode="elements")

    # 一次性加载整合文件
    docs = file_loader.load()

    print(docs)


if __name__ == '__main__':
    load_md()