FROM python:3.6

COPY ./dafni-run.sh /code/dafni-run.sh
COPY ./scripts/run.py /code/run.py
COPY ./scripts/dafni_script_config.ini /code/script_config.ini

RUN pip install cdcam

CMD bash /code/dafni-run.sh > /data/outputs/out.log 2> /data/outputs/err.log
