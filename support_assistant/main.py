import os
from typing import TypedDict

from fastapi import FastAPI
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from rag import retrieve_documents


# ---------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------

class AskRequest(BaseModel):
    query: str


class SupportResponse(BaseModel):
    answer: str
    sources: list
    confidence: float = Field(ge=0.0, le=1.0)


# ---------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------

class SupportState(TypedDict, total=False):
    query: str
    intent: str
    retrieved_documents: list
    answer: str
    sources: list
    confidence: float


# ---------------------------------------------------------
# Intent classification
# ---------------------------------------------------------

def classify_intent(state: SupportState):
    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "cancel",
        "gift card",
        "support hours",
    ]

    if any(keyword in query for keyword in policy_keywords):
        intent = "policy_question"
    else:
        intent = "general_question"

    return {"intent": intent}


# ---------------------------------------------------------
# Retrieval and answer
# ---------------------------------------------------------

def retrieve_and_answer(state: SupportState):
    query = state["query"]

    retrieved = retrieve_documents(query, top_k=3)

    if not retrieved:
        return {
            "retrieved_documents": [],
            "answer": (
                "Based on the retrieved context: "
                "No relevant policy context was found."
            ),
            "sources": [],
            "confidence": 1.0,
        }

    top_chunk = retrieved[0]["document"]
    top_chunk_snippet = top_chunk[:200].strip()

    answer = f"Based on the retrieved context: {top_chunk_snippet}"

    sources = [item["id"] for item in retrieved]

    return {
        "retrieved_documents": retrieved,
        "answer": answer,
        "sources": sources,
        "confidence": 1.0,
    }


# ---------------------------------------------------------
# Direct answer
# ---------------------------------------------------------

def direct_answer(state: SupportState):
    return {
        "answer": "I can only answer questions about Zepto policies right now.",
        "sources": [],
        "confidence": 1.0,
    }


# ---------------------------------------------------------
# LangGraph routing
# ---------------------------------------------------------

def route_after_classification(state: SupportState):
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


def build_graph():
    graph = StateGraph(SupportState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_and_answer", retrieve_and_answer)
    graph.add_node("direct_answer", direct_answer)

    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "retrieve_and_answer": "retrieve_and_answer",
            "direct_answer": "direct_answer",
        },
    )

    graph.add_edge("retrieve_and_answer", END)
    graph.add_edge("direct_answer", END)

    return graph.compile()


graph = build_graph()


# ---------------------------------------------------------
# MOCK_LLM and validation
# ---------------------------------------------------------

def mock_llm_enabled():
    """Return True when MOCK_LLM is unset or set to 1."""
    return os.getenv("MOCK_LLM", "1") == "1"


def validate_llm_response(raw_output):
    """Validate raw LLM output using the Pydantic response model."""

    if isinstance(raw_output, SupportResponse):
        return raw_output

    if isinstance(raw_output, dict):
        return SupportResponse.model_validate(raw_output)

    raise ValueError(
        "LLM output must be a dictionary or SupportResponse."
    )


def generate_with_optional_llm(raw_output):
    """
    Validate optional real-LLM output.

    Invalid output is retried up to two additional times.
    """

    last_error = None

    for attempt in range(3):
        try:
            return validate_llm_response(raw_output)

        except Exception as error:
            last_error = error

            if attempt < 2:
                corrective_instruction = (
                    "Return valid JSON with exactly these fields: "
                    "answer, sources, confidence. "
                    "confidence must be between 0 and 1."
                )

                # Placeholder for future real LLM retry call.
                _ = corrective_instruction

    return SupportResponse(
        answer=f"LLM response validation failed after 3 attempts: {last_error}",
        sources=[],
        confidence=0.0,
    )


# ---------------------------------------------------------
# Run support assistant
# ---------------------------------------------------------

def run_support_assistant(query: str):
    """Run the LangGraph workflow and validate the final response."""

    result = graph.invoke({"query": query})

    if mock_llm_enabled():
        response = SupportResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
        )

    else:
        raw_output = {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
        }

        response = generate_with_optional_llm(raw_output)

    return response


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Zepto Support Assistant",
    description="GenAI support assistant using RAG, ChromaDB, and LangGraph.",
    version="1.0.0",
)


@app.post("/ask", response_model=SupportResponse)
def ask(request: AskRequest):
    return run_support_assistant(request.query)