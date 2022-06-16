FROM python:3.8-alpine
RUN apk --update add gcc build-base
RUN pip install --no-cache-dir kopf kubernetes
WORKDIR /app
ADD milk.py /app
CMD kopf run /app/milk.py --all-namespaces