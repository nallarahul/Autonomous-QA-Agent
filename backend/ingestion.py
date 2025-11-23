import os
import shutil
from langchain_community.document_loaders import TextLoader, JSONLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Define paths
DB_PATH = "./vector_db"
UPLOAD_DIR = "./uploaded_docs"

class KnowledgeBase:
    def __init__(self):
        # using the miniLM model here since it's fast and decent for this kind of task
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def ingest_documents(self, source_files):
        """
        Processes uploaded files and stores them in ChromaDB.
        """
        documents = []
        
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        # we have to save these to disk first because the langchain loaders need actual file paths
        saved_paths = []
        for file in source_files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(file_path)

        # right now just handling standard text formats
        for path in saved_paths:
            if path.endswith(".md") or path.endswith(".txt") or path.endswith(".json"):
                loader = TextLoader(path, encoding="utf-8")
                documents.extend(loader.load())

        if not documents:
            return "No valid text documents found."

        # breaking the text into smaller chunks so the context window doesn't get maxed out
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        # actually creating the vector store and saving it locally
        db = Chroma.from_documents(
            documents=chunks, 
            embedding=self.embedding_function,
            persist_directory=DB_PATH
        )
        db.persist()

        # cleaning up the temp folder to keep things tidy
        for path in saved_paths:
            os.remove(path)
            
        return f"Successfully processed {len(chunks)} chunks from {len(source_files)} files."

    def get_retriever(self):
        # hooking back up to the existing db to run queries
        db = Chroma(persist_directory=DB_PATH, embedding_function=self.embedding_function)
        return db.as_retriever(search_kwargs={"k": 4})