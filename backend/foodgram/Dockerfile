
FROM python:3.9

WORKDIR /code
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip \
    && pip3 install -r /code/requirements.txt --no-cache-dir
COPY . .
CMD gunicorn foodgram.wsgi:applicationdocker build -t billglasses/gates:v2.11.1989 . --bind 0.0.0.0:8000