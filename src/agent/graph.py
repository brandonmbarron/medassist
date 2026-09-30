"""Week 2, Blocks 4 to 5: the MedAssist LangGraph agent.

Flow:
    redact -> classify -> route --urgent_clinical/complaint--> escalate
                              --benefits/prior_auth------> answer_from_docs -> safety_check
                              --claim_status-------------> lookup_claim     -> safety_check

Design rule: urgent/clinical messages NEVER reach the LLM answer path.
That rule is enforced in code (route), not in a prompt, so it can be tested.

Run:
    python -m src.agent.graph "Does my PPO-GOLD plan cover an MRI?"
"""

from __future__ import annotations

import sys
from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

from src.guardrails.redact import redact


class AgentState(TypedDict, total=False):
    raw_message: str
    member_id: str
    plan_id: str
    message: str          # redacted text; the only version the LLM ever sees
    intent: str
    confidence: float
    context: list[dict]   # retrieved chunks or claim rows
    answer: str
    citations: list[str]
    escalated: bool
    safety_flags: list[str]


ESCALATE_INTENTS = {"urgent_clinical", "complaint"}
MIN_CONFIDENCE = 0.6  # below this, a human looks at it


# ---------- nodes ----------

def redact_node(state: AgentState) -> AgentState:
    return {"message": redact(state["raw_message"])}


def classify_node(state: AgentState) -> AgentState:
    """TODO (you, Week 2 Block 5): load models/intent_distilbert with a
    transformers pipeline("text-classification") and return intent + score.
    Until the model is trained, this keyword stub keeps the graph runnable."""
    text = state["message"].lower()
    if any(w in text for w in ("chest pain", "breathing", "fell", "too much", "dizzy", "fever")):
        return {"intent": "urgent_clinical", "confidence": 0.9}
    if "claim" in text:
        return {"intent": "claim_status", "confidence": 0.7}
    if "authoriz" in text or "approval" in text:
        return {"intent": "prior_auth", "confidence": 0.7}
    return {"intent": "benefits", "confidence": 0.65}


def route(state: AgentState) -> Literal["escalate", "answer_from_docs", "lookup_claim"]:
    if state["intent"] in ESCALATE_INTENTS or state.get("confidence", 0) < MIN_CONFIDENCE:
        return "escalate"
    if state["intent"] == "claim_status":
        return "lookup_claim"
    return "answer_from_docs"


def escalate_node(state: AgentState) -> AgentState:
    if state["intent"] == "urgent_clinical":
        msg = ("If this is a medical emergency, call 911 now. "
               "I'm connecting you with a nurse line representative.")
    else:
        msg = "I'm connecting you with a member services representative who can help."
    # TODO (you): write the escalation to a review queue (a JSONL file is fine)
    return {"answer": msg, "escalated": True, "citations": []}


def answer_from_docs_node(state: AgentState) -> AgentState:
    """TODO (you):
      1. Call src.retrieval.index.search(state["message"]).
      2. Build a prompt that says: answer ONLY from the context, cite the
         section, say "I don't know" if it's not there, never give medical advice.
      3. Call your LLM (Anthropic or OpenAI SDK; read the API key from an env var).
      4. Return answer + citations like "ppo_gold_2026.md > Diagnostic imaging".
    """
    raise NotImplementedError("Week 2, Block 5: implement answer_from_docs_node")


def lookup_claim_node(state: AgentState) -> AgentState:
    """TODO (you): query data/curated/claims (pandas.read_parquet is fine here)
    for state["member_id"], summarize the most recent claims in plain language,
    and explain any denial_reason. Never return another member's data."""
    raise NotImplementedError("Week 2, Block 5: implement lookup_claim_node")


def safety_check_node(state: AgentState) -> AgentState:
    """Week 3, Block 1: see src/guardrails/safety.py."""
    from src.guardrails.safety import check_output
    flags = check_output(state.get("answer", ""), state.get("citations", []))
    if flags:
        return {"safety_flags": flags, "escalated": True,
                "answer": "I want to make sure you get accurate information, "
                          "so I'm connecting you with a representative."}
    return {"safety_flags": []}


# ---------- graph ----------

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("redact", redact_node)
    g.add_node("classify", classify_node)
    g.add_node("escalate", escalate_node)
    g.add_node("answer_from_docs", answer_from_docs_node)
    g.add_node("lookup_claim", lookup_claim_node)
    g.add_node("safety_check", safety_check_node)

    g.set_entry_point("redact")
    g.add_edge("redact", "classify")
    g.add_conditional_edges("classify", route)
    g.add_edge("answer_from_docs", "safety_check")
    g.add_edge("lookup_claim", "safety_check")
    g.add_edge("escalate", END)
    g.add_edge("safety_check", END)
    return g.compile()


if __name__ == "__main__":
    app = build_graph()
    msg = " ".join(sys.argv[1:]) or "I'm having chest pain right now"
    result = app.invoke({"raw_message": msg, "member_id": "M0000001", "plan_id": "PPO-GOLD"})
    for k, v in result.items():
        print(f"{k:>14}: {v}")
