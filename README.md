# MedAssist

A LangGraph agent that answers Medicare Advantage member questions, routes them safely, and escalates anything urgent or clinical to a human.

> All data in this repo is synthetic. No real member information is used anywhere.

<!-- TODO (Week 3): add a demo GIF and the eval scorecard here -->

## What it does

1. **Redacts PHI** before any model sees the message
2. **Classifies intent** with a fine-tuned DistilBERT model (benefits, claim status, prior auth, complaint, urgent/clinical)
3. **Routes** the message:
   - urgent/clinical or complaint → human escalation (enforced in code, not in a prompt)
   - benefits / prior auth → retrieval over plan documents, answer with citations
   - claim status → lookup over PySpark-curated claims data
4. **Safety-checks** every answer (grounded, no medical advice, no leaked identifiers)
5. **Logs** each run for evaluation and a monitoring dashboard

## Results

| Model | Macro F1 |
| --- | --- |
| TF-IDF + logistic regression | TODO |
| DistilBERT (fine-tuned) | TODO |

| Eval metric | Score | Threshold |
| --- | --- | --- |
| Routing accuracy | TODO | 80% |
| Escalation recall | TODO | 100% |

## Quickstart

```bash
make setup        # creates .venv and installs requirements
make data         # generates synthetic members, claims, messages
make etl          # PySpark pipeline -> data/curated/
make index        # builds the plan-document index
make baseline     # scikit-learn baseline
make train        # fine-tune DistilBERT (Colab GPU recommended)
make agent        # run one message through the agent
make eval         # scorecard; also runs in CI
make dashboard    # Streamlit monitoring
```

## Repo layout

```
scripts/generate_data.py   synthetic data
src/etl/                   PySpark pipeline + SQL
src/retrieval/             plan-document index
src/models/                baseline + DistilBERT
src/agent/                 LangGraph graph
src/guardrails/            redaction + output safety
eval/                      golden set + scorecard
app/dashboard.py           monitoring
docs/                      model card, business case, learning log
```

## Responsible AI

See [docs/model_card.md](docs/model_card.md) for intended use, limits, and known failure modes.
