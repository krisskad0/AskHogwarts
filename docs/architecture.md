# AskHogwarts - RAG-based Character Response System

## Project Architecture

### 1. System Overview
The AskHogwarts system is a FastAPI-based application that implements a Retrieval-Augmented Generation (RAG) pipeline to generate character-specific responses from Harry Potter and the Sorcerer's Stone. The system uses Pinecone for vector storage and LangChain for the RAG implementation.

### 2. Project Structure
```
app/
├── api/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── document.py       # PDF upload and processing endpoints
│   │   ├── question.py       # Question answering endpoints
│   │   └── character.py      # Character-related endpoints
│   └── dependencies/
│       └── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── security.py          # Authentication & authorization
│   └── logging.py           # Logging configuration
├── services/
│   ├── __init__.py
│   ├── pdf_processor.py     # PDF extraction and chunking
│   ├── vector_store.py      # Pinecone integration
│   ├── character_analyzer.py # Character trait analysis
│   └── response_generator.py # Response generation
├── models/
│   ├── __init__.py
│   ├── document.py          # Document-related schemas
│   ├── character.py         # Character-related schemas
│   └── response.py          # Response-related schemas
└── utils/
    ├── __init__.py
    └── text_processing.py   # Text processing utilities

tests/
├── unit/
└── integration/
```

### 3. Core Components

#### 3.1 API Layer
- **Document API** (`/api/documents/`)
  - POST `/upload`: Upload and process PDF
  - GET `/status/{document_id}`: Check processing status
  
- **Question API** (`/api/questions/`)
  - POST `/ask`: Submit question with character context
  - GET `/history`: Retrieve question history

- **Character API** (`/api/characters/`)
  - GET `/list`: List available characters
  - GET `/{character}/traits`: Get character traits

#### 3.2 Service Layer

##### PDF Processing Service
- Handles PDF extraction using PyPDF2/pdfplumber
- Implements text cleaning and preprocessing
- Manages document chunking for optimal retrieval
- Handles concurrent processing for large documents

##### Vector Store Service (Pinecone Integration)
- Manages document embeddings and storage
- Implements efficient vector search
- Handles batch processing and updates
- Implements caching for frequent queries

##### Character Analysis Service
- Analyzes character traits from text
- Maintains character context database
- Implements trait scoring and relevance

##### Response Generation Service
- Implements RAG pipeline using LangChain
- Manages prompt engineering
- Handles response formatting and validation

### 4. Data Flow

1. **PDF Upload Flow**
```mermaid
graph LR
    A[Client] --> B[Document API]
    B --> C[PDF Processor]
    C --> D[Text Chunks]
    D --> E[Vector Store]
    E --> F[Pinecone]
```

2. **Question Answering Flow**
```mermaid
graph LR
    A[Client] --> B[Question API]
    B --> C[Character Analyzer]
    C --> D[Vector Store]
    D --> E[Response Generator]
    E --> F[Client Response]
```

### 5. Technical Specifications

#### 5.1 Dependencies
- FastAPI for API framework
- LangChain for RAG pipeline
- Pinecone for vector storage
- PyPDF2/pdfplumber for PDF processing
- Pydantic for data validation
- uvicorn for ASGI server

#### 5.2 Configuration
- Environment-based configuration
- Configurable chunking parameters
- Adjustable retrieval parameters
- Customizable character traits

#### 5.3 Security
- API authentication
- Rate limiting
- Input validation
- Error handling

### 6. Scalability Considerations

#### 6.1 Performance Optimizations
- Caching frequently accessed vectors
- Batch processing for document uploads
- Async processing for long-running tasks
- Connection pooling for database operations

#### 6.2 Monitoring and Logging
- Request/response logging
- Performance metrics
- Error tracking
- Usage analytics

### 7. Deployment
- Docker containerization
- Kubernetes orchestration
- CI/CD pipeline
- Health checks and monitoring

### 8. Future Enhancements
- Character voice fine-tuning
- Multi-book support
- Response caching
- Advanced analytics
