FROM python:3.9-alpine
WORKDIR /bot
COPY . /bot
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD [ "python3", "bot.py" ]