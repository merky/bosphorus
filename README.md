# Bosphorus

## Requirements

 * Orthanc 0.7.5 (lightweight DICOM server)
 * Python  2.7   (along with libraries, see requirements.txt)
 * Docker  0.11  (for preferred deployment)

## Setup

Note: see [bosphorus-docker](http://github.com/merky/bosphorus-docker) for easy installation using docker containers.

Here's a simplified breakdown of installation:

 * Install/configure Orthanc (modify your `orthanc.config.json`)
 * Start Orthanc
 * Download orthancpy
```bash
git clone github.com/merky/orthancpy.git
```

 * Download Bosphorus and install libraries
```bash
git clone github.com/merky/bosphorus.git
cd bosphorus
pip install -r requirements.txt
```

 * Configure Bosphorus by modifying `bosphorus/settings.py`

## Run

```bash
python manage.py server
```
