FROM python:3.8
RUN mkdir /app
WORKDIR /app
COPY duneserver /app
RUN mkdir /dune
COPY dune /dune
RUN mkdir /duneclient
COPY duneclient /duneclient
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_ENV="docker"
EXPOSE 5000
CMD python app.py