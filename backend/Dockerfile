FROM python:3.9.13

WORKDIR /app

COPY requirements.txt .

RUN pip install gunicorn==20.1.0 && \
    pip install --no-cache-dir -r requirements.txt

COPY . ./

CMD [ "sh", "entrypoint.sh"]
# CMD ["gunicorn", "--bind", "0.0.0.0:9090", "foodgram.wsgi"]
