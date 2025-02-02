# app/Dockerfile
# docker build -t streamlit .
# docker build --no-cache -t streamlit .
# docker run -p 8501:8501 streamlit

FROM python:3.9-slim

WORKDIR /app

# Configurar locale pt_BR.UTF-8
ENV LANG=pt_BR.UTF-8 \
    LC_ALL=pt_BR.UTF-8

# Instalar dependências do sistema (incluindo locales)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Gerar a locale pt_BR.UTF-8
RUN echo "pt_BR.UTF-8 UTF-8" >> /etc/locale.gen \
&& locale-gen pt_BR.UTF-8

# Clonar repositório (com invalidação de cache)
ARG CACHEBUST=1
RUN git clone https://github.com/wagnerpiressilva/python-streamlit.git .

# Clone repository into a subdirectory and copy files to /app
#RUN git clone --branch main https://github.com/wagnerpiressilva/python-streamlit.git .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "1_Indicadores.py", "--server.port=8501", "--server.address=0.0.0.0"]