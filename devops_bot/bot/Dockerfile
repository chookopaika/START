FROM python:3.9-slim
WORKDIR /bot
COPY . .
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 1313
CMD [ "python3", "bot.py" ]