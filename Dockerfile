FROM neuro:latest

RUN apt-get update && apt-get install -y -qq graphviz

ADD ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

