# MedAssist model card

Fill this in during Week 3. Interviewers for responsible-AI teams read this closely.

## Intended use
Portfolio demonstration of a member-services triage agent. Not for real members or real clinical use.

## Components
- Intent classifier: DistilBERT fine-tuned on synthetic messages (TODO: metrics)
- Retrieval: Chroma over fictional plan summaries
- LLM: TODO (provider, model, temperature)

## Safety design
- PHI redacted before model input and logging
- Urgent/clinical intents routed to humans in code
- Low-confidence classifications escalated
- Answers must cite a plan-document section

## Known limitations
- Training messages are template-generated, so real-world accuracy will be lower
- TODO: failure cases found during evaluation

## Evaluation
TODO: golden set size, metrics, thresholds, date run
