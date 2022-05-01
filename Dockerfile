FROM python

COPY . ./Valorant-Store

WORKDIR ./Valorant-Store

RUN pip install -r requirements.txt

CMD ["python", "./bot.py"]
