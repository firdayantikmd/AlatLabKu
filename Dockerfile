FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh

ENV FLASK_ENV development
ENV FLASK_DEBUG 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-u", "run.py"]
