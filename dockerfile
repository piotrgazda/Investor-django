FROM python:3.10
ENV PYTHONUNBUFFERED=1


WORKDIR /app
COPY requirements.txt /app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app

CMD [ "python" ,"investor/manage.py", "runserver", "0.0.0.0:8000"  ]