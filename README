# Image Catalog

## Purpose
This library is a tool that i started to find and catalog all images that
we accumulated over the years on many devices.

The idea is to read and catalog all images and videos in elastic.
In the first instance, there are the following functionalities foreseen

* Catalog image and video files. Add new locations to catalg
* Reorganize image files on disk, based on image data (exif)
* Find duplicates
* Specify what to do with the duplicates
  * Delete duplicates in the same location (directory)
  * Keep duplicates in specific locations (e.g. at least 2 copies)
* Find not exact duplicates, but images that differ only in resolution but the image is the same
* Find highly similar images and choose one
* Find images that do not contain anything interesting (blanks, bad pics)

### Prerequisites

* Python 3
* A running elasticsearch instance on a host:port that is reachable. A working docker-compose.yml is in the docker directory.


### Catalog Files

Using the add_to_catalog script, it is already possible to populate elastic with data.

Usage:
```
usage: add_to_catalog.py [-h] [--recursive] [--allow_duplicates] [--host HOST]
                         [--port PORT]
                         dirname

Catalog all image and video files in the given directory

positional arguments:
  dirname               name of directory to catalog

optional arguments:
  -h, --help            show this help message and exit
  --recursive, -r       recurse into subdirectories. Default: false
  --allow_duplicates, -d
                        Duplicates are not ok by default.
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200

```

