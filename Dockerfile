# app/Dockerfile

FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y pkg-config libz-dev \
    build-essential \
    libssl-dev \
    curl \
    software-properties-common \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/willpettengill/dailyheavens.git /app
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel
RUN pip3 install -r /app/requirements.txt

EXPOSE 80


HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "heavens-app.py", "--server.port=80", "--server.address=0.0.0.0"]
