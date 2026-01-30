FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x wait-for-it.sh

ENV PYTHONPATH=/app
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=development

EXPOSE 3000

CMD ["sh", "-c", "./wait-for-it.sh postgres:5432 -- uvicorn backend.app:app --reload --host=0.0.0.0 --port=3000"]