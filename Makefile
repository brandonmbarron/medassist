.PHONY: setup data etl index baseline train agent eval test dashboard

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

data:
	python scripts/generate_data.py

etl:
	python -m src.etl.pipeline

index:
	python -m src.retrieval.index

baseline:
	python -m src.models.baseline

train:
	python -m src.models.train_intent

agent:
	python -m src.agent.graph "Does my PPO-GOLD plan cover an MRI?"

eval:
	python -m eval.run_eval --routing

test:
	python -m pytest -q

dashboard:
	streamlit run app/dashboard.py
