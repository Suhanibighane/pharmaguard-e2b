FROM python:3.10-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment restrictions require < 8gb memory, vcpu=2, runtime < 20m.
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
