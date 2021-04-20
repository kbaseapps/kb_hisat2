FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

RUN apt-get update --fix-missing
RUN apt-get install -y wget

# Here we install a python coverage tool and an
# https library that is out of date in the base image.

RUN pip install --upgrade pip \
    && python --version

RUN pip install coverage==5.5

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module
RUN sh /kb/module/install-hisat.sh

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
