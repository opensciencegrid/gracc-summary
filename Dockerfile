FROM python:3.8.5-alpine

# Needed to install requirements from github
RUN apk add --no-cache git

WORKDIR /gracc-summary
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
RUN python setup.py install

CMD /usr/local/bin/graccsumperiodic
