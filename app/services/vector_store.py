from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain.schema import Document
from app.core.config import Settings


class VectorStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """
        Ensure the Pinecone index exists, create if it doesn't.
        """
        # List existing indexes
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        # Create index if it doesn't exist
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='gcp',
                    region='us-central1'
                )
            )

    async def upsert_documents(self, documents: List[Document]) -> Dict:
        """
        Upsert documents into Pinecone index.
        Latest version of Pinecone handles embeddings automatically.
        
        Args:
            documents: List of Document objects containing text and metadata
            
        Returns:
            Dictionary with upsert status
        """
        index = self.pc.Index(self.index_name)
        
        # Prepare documents for upsert
        vectors = []
        for i, doc in enumerate(documents):
            vectors.append({
                "id": f"doc_{i}",
                "text": doc.page_content,
                "metadata": {
                    **doc.metadata,
                    "chunk_id": i
                }
            })
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                index.upsert(vectors=batch)
            except Exception as e:
                print(f"Error upserting batch {i//batch_size}: {str(e)}")
                raise
        
        return {"status": "success", "documents_processed": len(documents)}

    async def query(
        self,
        query_text: str,
        character: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Query the vector store for relevant documents.
        
        Args:
            query_text: The query text
            character: Optional character name to filter results
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with scores
        """
        index = self.pc.Index(self.index_name)
        
        # Prepare filter if character is specified
        filter_dict = {"character": character} if character else None
        
        # Query the index
        results = index.query(
            query_texts=[query_text],
            top_k=top_k,
            filter=filter_dict
        )
        
        return results.to_dict()["matches"]
