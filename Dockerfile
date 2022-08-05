FROM python:3.9

ENV PYTHONUNBUFFERED True

EXPOSE 8080

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

CMD streamlit run --server.port 8080 --server.enableCORS false home.py

