FROM python:3.7-slim-stretch

RUN apt-get update &&\
    apt-get install -y git gcc &&\
    pip install requests reportlab lxml

WORKDIR /usr/src
RUN git clone --depth 1 https://github.com/dinosauria123/gcv2hocr.git &&\
    git clone --depth 1 https://github.com/tmbdev/hocr-tools.git &&\
    git clone --depth 1 https://github.com/kozakana/gcvpdf.git &&\
    cp gcv2hocr/gcv2hocr.py gcvpdf/ &&\
    cp hocr-tools/hocr-pdf gcvpdf/hocr_pdf.py

WORKDIR /usr/src/gcvpdf

#ENTRYPOINT python app.py
