# Imagem base leve para Python 3.10
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema para compilação (necessário para algumas libs de data science)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os requisitos e instala as bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para dentro do container
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o app (as variáveis de porta são passadas no docker-stack)
CMD ["streamlit", "run", "shadow_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]