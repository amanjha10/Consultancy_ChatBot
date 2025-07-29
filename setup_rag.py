import json
import os
import uuid
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class RAGSystem:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', persist_directory: str = 'data/vectors/chroma'):
        """Initialize the RAG system"""
        try:
            # Initialize the embedding model
            self.model = SentenceTransformer(model_name)
            
            # Ensure persist directory exists and is absolute
            self.persist_directory = os.path.abspath(persist_directory)
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB with settings
            settings = Settings(
                anonymized_telemetry=False,  # Disable telemetry to avoid errors
                allow_reset=True,  # Allow resetting the database
                is_persistent=True
            )
            
            # Create ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=settings
            )

            # Try to get existing collection or create new one
            try:
                self.collection = self.client.get_collection(name="study_abroad_docs")
            except ValueError:
                # Collection doesn't exist, create new one
                self.collection = self.client.create_collection(
                    name="study_abroad_docs",
                    metadata={"hnsw:space": "cosine"}
                )
            
            self.is_initialized = True
            print("RAG system initialized successfully")
            
        except Exception as e:
            print(f"Error initializing RAG system: {e}")
            self.is_initialized = False
            raise

    def load_documents(self, json_path: str) -> bool:
        """Load documents into ChromaDB"""
        if not self.is_initialized:
            print("RAG system not properly initialized")
            return False

        try:
            # Load and validate JSON
            if not os.path.isfile(json_path):
                raise FileNotFoundError(f"Document file not found: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process documents
            documents = []
            metadatas = []
            ids = []
            
            # Flatten the nested structure
            for category, subcategories in data.items():
                for subcategory, items in subcategories.items():
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict) and 'question' in item and 'answer' in item:
                                # Create document text
                                doc_text = f"{item['question']} {item['answer']}"
                                
                                # Create metadata
                                metadata = {
                                    'question': item['question'],
                                    'answer': item['answer'],
                                    'category': category,
                                    'subcategory': subcategory,
                                    'section': item.get('section', ''),
                                    'document': item.get('document', ''),
                                }
                                
                                # Generate unique ID
                                doc_id = item.get('chunk_id', str(uuid.uuid4()))
                                
                                documents.append(doc_text)
                                metadatas.append(metadata)
                                ids.append(doc_id)
            
            if not documents:
                print("No valid documents found to process")
                return False
            
            # Generate embeddings
            embeddings = self.model.encode(documents).tolist()
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Successfully loaded {len(documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error loading documents: {e}")
            return False

    def search(self, query: str, k: int = 3) -> List[dict]:
        """Search for relevant documents"""
        if not self.is_initialized:
            print("RAG system not properly initialized")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query]).tolist()[0]
            
            # Search the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Process results
            documents = []
            for i, (meta, doc, distance) in enumerate(zip(
                results['metadatas'][0],
                results['documents'][0],
                results['distances'][0]
            )):
                # Convert distance to similarity score (1 - distance)
                score = 1.0 - distance
                
                # Create result object
                result = {
                    **meta,
                    'score': round(score, 4),
                    'rank': i + 1,
                    'raw_text': doc
                }
                documents.append(result)
            
            return documents
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    @classmethod
    def load(cls, directory: str):
        """Load a RAG system with existing vectors"""
        return cls(persist_directory=directory + '/chroma')

if __name__ == '__main__':
    # Test the system
    rag = RAGSystem()
    success = rag.load_documents('data/documents/education_faq.json')
    print(f"Documents loaded successfully: {success}")
    
    if success:
        test_query = "Why study abroad?"
        results = rag.search(test_query)
        print(f"\nTest Query: {test_query}")
        print("\nTop relevant documents:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['score']:.2f}")
            print(f"Q: {result['question']}")
            print(f"A: {result['answer']}")
