FROM python:3.10.11-slim-bullseye

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./ 
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]