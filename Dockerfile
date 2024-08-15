FROM python:3.11-slim-buster

WORKDIR /app

#################################################################################
# Install git
RUN apt-get update && apt-get install -y git

# as long as the sgr_library is not published as pip module:
COPY . .
RUN pip install -r sgr/requirements.txt
#RUN pip install xsdata[cli]

# generate data classes
#RUN xsdata --package data_classes sgr/xsd_files/SGrIncluder.xsd

#################################################################################
RUN pip install -r requirements.txt
RUN pip install -e sgr

CMD ["python", "main.py"]