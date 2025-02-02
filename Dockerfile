# app/Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone repository into a subdirectory and copy files to /app
RUN git clone https://github.com/wagnerpiressilva/python-streamlit.git repo \
    && cp -a repo/. /app \
    && rm -rf repo

RUN ls -la

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "1_Indicadores.py", "--server.port=8501", "--server.address=0.0.0.0"]