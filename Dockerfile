FROM python:3.12-slim-bookworm

# install dependencies
RUN pip install -r requirements.txt

WORKDIR /app

# copy application files
COPY . .

CMD [ "python", "main.py"]
