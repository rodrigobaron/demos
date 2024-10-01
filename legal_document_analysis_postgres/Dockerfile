FROM python:3.12.4

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# CMD ["python", "rrf.py"]
ENTRYPOINT [ "bash" ]
# CMD ["bash"]