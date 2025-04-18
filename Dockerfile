FROM python:3.11-slim

WORKDIR /app

COPY marquee.py .

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests

CMD ["python", "marquee.py"]

