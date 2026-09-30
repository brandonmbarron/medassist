# Week 3, Block 3. TODO (you): add a docker-compose.yml that runs the
# dashboard, and a .dockerignore that excludes data/ and models/.
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/dashboard.py", "--server.address=0.0.0.0"]
