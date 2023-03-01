FROM python:3.9

WORKDIR /app
COPY collector.py config.py githubapi.py githubcachemetrics.py requirements.txt config.yaml ./

RUN pip install -r requirements.txt

CMD python collector.py