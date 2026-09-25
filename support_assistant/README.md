# Zepto Support Assistant

A small GenAI support assistant for Zepto built using Retrieval-Augmented Generation (RAG), Sentence Transformers, ChromaDB, LangGraph, Pydantic, and FastAPI.

## 1. Project Overview

The Support Assistant answers Zepto policy-related customer questions using a fixed 8-document policy corpus.

The system:

1. Loads the Zepto policy documents.
2. Creates embeddings using the local `all-MiniLM-L6-v2` Sentence Transformer model.
3. Stores the embeddings in ChromaDB.
4. Classifies the customer query as either a policy question or a general question.
5. Retrieves the top 3 relevant policy chunks for policy questions.
6. Generates a deterministic mock response when `MOCK_LLM` is unset or set to `1`.
7. Validates the final response using Pydantic.
8. Provides the assistant through a FastAPI `/ask` endpoint.

## 2. Architecture

The main data flow is:

```text
8 Policy Documents
        |
        v
Document Loading
        |
        v
Chunking
        |
        v
Sentence Transformer
all-MiniLM-L6-v2
        |
        v
ChromaDB
zepto_policy_corpus
        |
        v
Customer Query
        |
        v
classify_intent
        |
        +-----------------------------+
        |                             |
        | policy_question              | general_question
        v                             v
retrieve_and_answer              direct_answer
        |                             |
        v                             v
Top 3 Chroma Results              Fixed Response
        |                             |
        +-------------+---------------+
                      |
                      v
               Pydantic Validation
                      |
                      v
                 FastAPI /ask
```

## 3. Files and Functions

### `rag.py`

Responsible for document ingestion, embedding, ChromaDB storage, and retrieval.

Important functions:

* `load_documents()` - loads the 8 policy documents from the `docs` folder.
* `chunk_documents()` - creates one chunk for each policy document.
* `build_vector_database()` - creates embeddings and stores them in ChromaDB.
* `retrieve_documents()` - embeds the query and retrieves the top 3 documents using cosine similarity.

Embedding model:

```text
all-MiniLM-L6-v2
```

ChromaDB collection:

```text
zepto_policy_corpus
```

### `prompt.py`

Contains the structured support assistant prompt.

The prompt includes:

* ROLE
* CONTEXT
* TASK
* FORMAT
* LENGTH
* NEGATIVE CONSTRAINT
* FEW-SHOT EXAMPLE

The function:

```text
build_support_prompt()
```

creates the final prompt using the customer query and retrieved context.

### `main.py`

Contains the LangGraph workflow and FastAPI application.

Important functions:

* `classify_intent()`
* `retrieve_and_answer()`
* `direct_answer()`
* `route_after_classification()`
* `build_graph()`
* `mock_llm_enabled()`
* `validate_llm_response()`
* `generate_with_optional_llm()`
* `run_support_assistant()`

LangGraph nodes:

```text
classify_intent
retrieve_and_answer
direct_answer
```

The graph starts with `classify_intent`.

A conditional edge sends:

```text
policy_question -> retrieve_and_answer
general_question -> direct_answer
```

## 4. Intent Classification

The mock intent classifier checks the lowercased customer query for these policy keywords:

```text
delivery
return
refund
membership
tracking
cancel
gift card
support hours
```

If any keyword is present:

```text
policy_question
```

Otherwise:

```text
general_question
```

## 5. Retrieval

For policy questions, the system:

1. Creates an embedding for the query.
2. Searches the ChromaDB collection.
3. Retrieves the top 3 results.
4. Uses the highest-ranked result as the top context chunk.
5. Creates a deterministic mock answer from the top chunk.

Mock retrieval response format:

```text
Based on the retrieved context: <top chunk snippet>
```

The top chunk snippet is limited to approximately 200 characters.

## 6. Mock LLM Mode

The project uses deterministic mock mode by default.

When `MOCK_LLM` is unset or set to:

```text
MOCK_LLM=1
```

no external LLM or network call is made for generation.

For policy questions, retrieval is still performed using the real embedding model and ChromaDB.

For general questions, the fixed response is:

```text
I can only answer questions about Zepto policies right now.
```

## 7. Optional Real LLM Path

The code contains an optional real-LLM validation path for:

```text
MOCK_LLM=0
```

The generated output is validated using the Pydantic `SupportResponse` model.

The validation logic allows up to 3 total attempts:

* Initial validation attempt
* First retry with corrective instructions
* Second retry with corrective instructions

If validation still fails, the system returns a clearly marked validation error with confidence `0.0`.

No external LLM provider is required for the default project demonstration.

## 8. Final Response Schema

The API response is validated using Pydantic.

Fields:

```text
answer: str
sources: list
confidence: float
```

`confidence` must be between `0.0` and `1.0`.

Example:

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials...",
  "sources": [
    "doc_01_chunk_01",
    "doc_05_chunk_01",
    "doc_03_chunk_01"
  ],
  "confidence": 1.0
}
```

## 9. FastAPI API

Start the application with:

```bash
uvicorn main:app --reload --port 7860
```

The API is available at:

```text
http://127.0.0.1:7860
```

Swagger documentation:

```text
http://127.0.0.1:7860/docs
```

### Endpoint

```text
POST /ask
```

Request format:

```json
{
  "query": "What is the delivery fee for orders below INR 149?"
}
```

## 10. Example API Calls

### Example 1 - Policy / Retrieval Question

Request:

```json
{
  "query": "What is the delivery fee for orders below INR 149?"
}
```

Response:

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01_chunk_01",
    "doc_05_chunk_01",
    "doc_03_chunk_01"
  ],
  "confidence": 1.0
}
```

### Example 2 - General Question

Request:

```json
{
  "query": "Tell me a joke."
}
```

Response:

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

Both examples run in the default mock mode.

## 11. Corpus

The system uses exactly 8 policy documents:

```text
docs/
├── doc_01.txt
├── doc_02.txt
├── doc_03.txt
├── doc_04.txt
├── doc_05.txt
├── doc_06.txt
├── doc_07.txt
└── doc_08.txt
```

The documents cover:

* Delivery
* Returns and refunds
* Membership
* Rider tracking
* Order cancellation
* Damaged or missing items
* Gift cards
* Customer support

## 12. ChromaDB

The vector database is stored locally in:

```text
chroma_db/
```

Collection name:

```text
zepto_policy_corpus
```

Cosine similarity is used for retrieval.

The vector database is built by running:

```bash
python rag.py
```

Expected output:

```text
Embedded and stored 8 chunks in ChromaDB.
```

## 13. Docker

The project includes a `Dockerfile`.

Build the image from the `support_assistant` directory:

```bash
docker build -t zepto-support-assistant .
```

Run the container:

```bash
docker run -p 7860:7860 zepto-support-assistant
```

The FastAPI application will then be available at:

```text
http://localhost:7860/docs
```

The Docker container runs Uvicorn on port `7860`.

## 14. Project Structure

```text
support_assistant/
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
├── chroma_db/
├── main.py
├── prompt.py
├── rag.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## 15. Running the Project Locally

From the `support_assistant` directory:

### Install dependencies

```bash
pip install -r requirements.txt
```

### Build the vector database

```bash
python rag.py
```

### Start FastAPI

```bash
uvicorn main:app --reload --port 7860
```

### Open Swagger

```text
http://127.0.0.1:7860/docs
```

The default configuration uses deterministic mock mode and does not require an API key or external LLM service.
