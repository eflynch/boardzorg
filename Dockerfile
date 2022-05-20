FROM python:3.8
RUN mkdir /app
WORKDIR /app
COPY server /app
RUN mkdir /boardzorg
COPY boardzorg /boardzorg
RUN mkdir /client
COPY client /client
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_ENV="docker"
EXPOSE 5000
CMD python app.py