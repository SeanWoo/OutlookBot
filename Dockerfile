FROM python:3.8
RUN apt-get update
WORKDIR /usr/src/outlookBot
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python","main.py"]