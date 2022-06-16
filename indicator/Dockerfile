FROM python:3.8-alpine
RUN apk --update add gcc build-base
RUN pip install --no-cache-dir kopf kubernetes
WORKDIR /app
ADD indicator.py /app
CMD kopf run /app/indicator.py --all-namespaces