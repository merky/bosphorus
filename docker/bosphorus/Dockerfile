# Ubuntu 12.04 LTS
FROM ubuntu:12.04

# Update
RUN apt-get -y update

# Install everything
RUN apt-get install -y python python-virtualenv python-pip \
                       git build-essential

# graph bosphorus source
RUN git clone https://github.com/merky/bosphorus.git
RUN git clone https://github.com/merky/orthancpy.git

# work in app dir
WORKDIR /bosphorus

# give permissions to run
RUN chmod +x manage.py

# add orthancpy
RUN ln -s -T ../orthancpy orthancpy

# make python environment
RUN pip install virtualenv && \
	virtualenv  env        && \
    . env/bin/activate     && \
    pip install -r requirements.txt

# local storage (mount at runtime)
VOLUME /data

# set up database
RUN env/bin/python manage.py initdb fake_names.txt

# entrypoint
ENTRYPOINT ["env/bin/python","manage.py"]
CMD ["server"]
