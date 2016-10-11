FROM daocloud.io/python:3-onbuild
RUN echo "Asia/Shanghai" > /etc/timezone
EXPOSE 8000
CMD [ "python", "./app.py"  ]
