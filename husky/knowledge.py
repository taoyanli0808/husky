
import tempfile
import threading

from io import BytesIO
from pathlib import Path
from typing import List, Dict

from loguru import logger

from llama_index.core import Settings, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PDFReader, DocxReader, MarkdownReader


# 初始化知识库 (单例模式)
class Knowledge:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._init_knowledge_base()
            return cls._instance
    
    def _init_knowledge_base(self):
        # 配置本地嵌入模型
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            cache_folder="./embed_models"
        )
        
        # 初始化存储
        self.storage_path = Path("./storage")
        self.storage_path.mkdir(exist_ok=True)
        
        try:
            self.storage_context = StorageContext.from_defaults(
                persist_dir=self.storage_path
            )
            self.index = load_index_from_storage(self.storage_context)
        except:
            self.storage_context = StorageContext.from_defaults()
            self.index = VectorStoreIndex([], storage_context=self.storage_context)
        
        # 文件解析器
        self.readers = {
            'application/pdf': PDFReader(),
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DocxReader(),
            'text/markdown': MarkdownReader()
        }
        
        # 文本分块
        self.splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    
    def add_files(self, files: List[BytesIO], mime_types: List[str]) -> Dict:
        """处理上传文件并更新索引"""
        new_docs = []
        for file, mime_type in zip(files, mime_types):
            # 安全检查
            if mime_type not in self.readers:
                continue
            
            # 使用临时文件处理（避免内存泄露）
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                file.save(tmp.name)
                try:
                    docs = self.readers[mime_type].load_data(Path(tmp.name))
                    nodes = self.splitter(docs)
                    new_docs.extend(nodes)
                except Exception as e:
                    logger.error(f"文件解析失败: {str(e)}")
        
        # 增量更新索引
        if new_docs:
            self.index.insert_nodes(new_docs)
            self.storage_context.persist(persist_dir=self.storage_path)
        
        return {"status": "success", "added_nodes": len(new_docs)}
    
    def query(self, question: str, top_k: int = 3) -> List[Dict]:
        """执行语义检索"""
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(question)
        return [{
            "text": node.text,
            "score": node.score,
            "metadata": node.metadata
        } for node in results]
