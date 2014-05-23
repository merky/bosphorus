# Bosphorus

## Requirements

 * Orthanc 0.7.5 (lightweight DICOM server)
 * Python  2.7   (along with libraries, see requirements.txt)
 * Docker  0.11  (for preferred deployment)

## Docker Deployment
This will ease the setup involved and make the entire stack a bit more
portable.

### Build images

Build the Orthanc docker image (relative to root dir)

    cd <root>/docker/orthanc
    sudo docker build -t orthanc .

Build the Bosphorus docker image (relative to root dir)

    cd <root>/docker/bosphorus
    sudo docker build -t bosphorus .

### Data Storage

If you want to use local storage (for both orthanc and bosphorus DB storage), 
make a local directory that will serve to mount to the running containers. Volume
mounts will need to be made to '/data' within the containers itself.

    mkdir <root>/data-store

move your orthanc config file there.

    cp orthanc.config.json ./data-store/

### Run Containers

Run Orthanc. Expose 8042 (HTTP).

    sudo docker run -v <root>/data-store:/data -p 8042:8042 orthanc

Run Bosphorus. Expose 80 (HTTP).


