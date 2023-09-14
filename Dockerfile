# app/Dockerfile

FROM python:3.9-slim
#FROM continuumio/miniconda3
#FROM gcc:4.9
WORKDIR /app

# Copy both requirements files into the container
#COPY pip-requirements.txt /app/pip-requirements.txt
#COPY conda-requirements.txt /app/conda-requirements.txt



# Install conda packages
#RUN conda env create -n heavens -f /app/conda-requirements.txt
#RUN conda create -n heavens python=3.9.7 
#RUN conda init bash
#RUN conda activate heavens
# Install pip packages

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
RUN dpkg -l | grep build-essential
ENV CC=/usr/bin/gcc
ENV CXX=/usr/bin/g++


RUN python -m pip install --upgrade pip setuptools wheel
RUN pip3 install -r /app/requirements.txt



ENV PATH=/usr/local/lib/python3.9/site-packages/flatlib/resources/swefiles:$PATH 
# seas_18.se1

EXPOSE 80


HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

#ENTRYPOINT ["streamlit", "run", "heavens-app.py", "--server.port=80", "--server.address=0.0.0.0"]
ENTRYPOINT ["python", "-m", "streamlit","run", "heavens-app.py", "--server.port=80", "--server.address=0.0.0.0"]
