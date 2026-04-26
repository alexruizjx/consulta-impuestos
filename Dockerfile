FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-spa
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--timeout", "300", ...]
