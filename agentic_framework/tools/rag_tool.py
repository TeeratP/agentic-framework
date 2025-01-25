# import os
# import asyncio
# from langchain_chroma import Chroma
# from langchain.tools import StructuredTool

# class ChromaDB:
#     def __init__(self, db_dir, collection_name, llm_emb):
#         self.db_dir = db_dir
#         self.collection_name = collection_name
#         self.llm_emb = llm_emb
        
#         # Create a new Chroma database if one does not already exist
#         if not os.path.exists(db_dir):
#             os.makedirs(db_dir)
#             self.db = Chroma(collection_name=collection_name, embedding_function=llm_emb, persist_directory=db_dir)
#         else:
#             self.db = Chroma(collection_name=collection_name, persist_directory=db_dir)
            
#     def add_doc(self, docs):
#         asyncio.run(self._add_doc_async(docs))
    
#     async def _add_doc_async(self, docs):
#         for doc in docs:
#             await self.db.aadd_document(doc)