FROM python:3.13-slim

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade  -r /requirements.txt

COPY ./src /src

EXPOSE 8000

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]