FROM python:3.8-alpine
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "./bot.py"]
