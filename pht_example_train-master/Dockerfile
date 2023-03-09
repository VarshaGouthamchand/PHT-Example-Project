FROM python:3.7

WORKDIR /app

RUN touch input.txt
RUN touch output.txt

COPY requirements.txt /app

RUN pip install -r requirements.txt

ADD ./javaTool /app/javaTool

COPY run_sparql_for_TRAIN.py /app

CMD ["python3", "run_sparql_for_TRAIN.py"]