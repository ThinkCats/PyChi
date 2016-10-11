FROM daocloud.io/python:3-onbuild
RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
EXPOSE 8000
CMD [ "python", "./app.py"  ]
