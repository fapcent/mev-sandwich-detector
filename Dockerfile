FROM python:3.9-slim

WORKDIR /app

# 1. Installation des outils de diagnostic (curl)
RUN apt-get update && apt-get install -y curl

# 2. Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pour voir les logs immédiatement
ENV PYTHONUNBUFFERED=1

CMD ["python", "whale_detector.py"]