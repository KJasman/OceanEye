FROM python:3.11

WORKDIR /usr/src/Spectral_Detection/

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

