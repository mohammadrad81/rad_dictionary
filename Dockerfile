FROM python:3.12-alpine
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir application
COPY main.py application
# COPY .env application
WORKDIR application
# CMD ["ls", "-lath", "app"]
CMD ["python", "main.py"]