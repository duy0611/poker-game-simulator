FROM python:3.7-slim

RUN mkdir -p /app
WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY app.py ./
COPY agent-build ./agent-build/
COPY static_files ./static_files/
COPY templates ./templates/
COPY src/ ./src/

EXPOSE 5000

CMD ["python", "./app.py"]