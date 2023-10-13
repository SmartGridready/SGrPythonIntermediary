FROM python:3.8-slim-buster

WORKDIR /app

#################################################################################
# as long as the sgr_library is not published as pip module:
COPY sgr sgr
RUN pip install -r sgr/requirements.txt
RUN pip install xsdata[cli]

# generate data classes
RUN xsdata --package data_classes sgr/xsd_files/SGrIncluder.xsd

#################################################################################
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY main.py main.py
CMD [ "python3", "-u" , "main.py"]