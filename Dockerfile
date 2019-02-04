FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

RUN apt-get install wget
# install hisat
ARG VERSION='2.1.0'
ENV PATH=$PATH:${pwd}/hisat2-${VERSION}
RUN rm -rf hisat-${VERSION}* &&\
    wget -q "ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/downloads/hisat2-${VERSION}-Linux_x86_64.zip" &&\
    unzip -q hisat2-${VERSION}-Linux_x86_64.zip &&\
    rm hisat2-${VERSION}-Linux_x86_64.zip &&\
    hisat2 --version

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
