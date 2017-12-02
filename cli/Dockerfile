FROM python:2.7-alpine
MAINTAINER David L. Chandler <immaculaterhelp@gmail.com>

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV INSTALL_PATH /todo
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN apk add --no-cache --virtual .build-deps \
  build-base ca-certificates \
    && pip install -r requirements.txt \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

COPY . .

CMD ["python2", "./todo-runner.py", "--help"]
