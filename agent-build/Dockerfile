FROM python:3.7-slim

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY app.py ./
COPY src/ ./src/

EXPOSE 5000

CMD ["python", "./app.py"]