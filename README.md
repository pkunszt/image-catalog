# Image Catalog

## Purpose
This library is a tool that i started to find and catalog all images that
we accumulated over the years on many devices.

The idea is to read and catalog all images and videos in elastic.
In the first instance, there are the following functionalities

* Catalog image and video files. Add new locations to catalog, import our old catalog, preserving
names that were given to subfolders and files therein
* Reorganize image files on disk, based on image data (exif)
* Deal with duplicates automatically. Have always 2 copies : dropbox and NAS

To Come:
* Find images that do not contain anything interesting (blanks, bad pics)
* Find not exact duplicates, but images that differ only in resolution but the image is the same
* Find highly similar images and choose one
* Identify people in images and tag them automatically

### Prerequisites

* Python 3
* A running elasticsearch instance on a host:port that is reachable. 
A working docker-compose.yml is in the docker directory, just spin up elastic and kibana
directly from there using `docker-compose up -d`
* A `config.json` file with the token for dropbox and the root locations of the catalog path.
A config-template.json is available, edit and save it as config.json

## Catalog Tools
Several local executables are available to perform all cataloguing work.
* Import old catalog to new one (one timer, this is only useful to me): `import_old_catalog`
* Uplopad files to catalog: `upload_to_catalog`  : upload images to the catalog locations, 
to the right directory with the right name
* Add files to elastic only: `add_to_elastic`  : add images in current location to elastic, but do not 
move it into the catalog locations yet. This is useful to see if data is already in the catalog or not, 
because items that have been catalogued already are reported.
* Sync nas to dropbox: `sync_nas_with_dropbox` : the `add_to_catalog` and `import_old_catalog` can upload also to dropbox in one go but
it is not the default as syncing to dropbox is slow. This does the dropbox sync and can be run 
overnight in the background. Dropbox is anyway only the cloud backup of everything for the case the nas burns down and not useful for anything else.
* Sync catalog with disk: `sync_catalog_with_disk`: Check that the catalog on disk and the catalog in 
elastic are in sync.

### Import Old Catalog
We have our old catalog layout with year, month as names. Some directories have already been added
with descriptive names to create 'albums', those are kept. Duplicates are removed and some more images
and videos renamed to contain the date and location of the image or video taken.


```
usage: import_old_catalog.py [-h] [--dropbox] [--nas_root NAS_ROOT]
                             [--dropbox_root DROPBOX_ROOT] [--month MONTH]
                             [--host HOST] [--port PORT] [--index INDEX]
                             basedir year

Import old catalog into new one. The directory structure has meaning here. The
data will be taken from the old structure down. Starting from a YEAR we will
traverse into the given months and subdirs are kept as such. Duplicates in the
same dir are not stored, but duplicates in named directories outside of month
are.

positional arguments:
  basedir               Base directory of old catalog.
  year                  Year to import.

optional arguments:
  -h, --help            show this help message and exit
  --dropbox             Also create the dropbox copy. Defaults to FALSE
  --nas_root NAS_ROOT   Use this as catalog root on NAS
  --dropbox_root DROPBOX_ROOT
                        Use this as catalog root on Dropbox
  --month MONTH         Only catalog the given month.
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic to use. Defauls to catalog

```

### Upload Files to Catalog
This script will upload the files in a given directory into the catalog. The files
will not be removed unless explicitly mentioned.
```
usage: upload_to_catalog.py [-h] [--recursive] [--dropbox]
                            [--nas_root NAS_ROOT]
                            [--dropbox_root DROPBOX_ROOT] [--host HOST]
                            [--port PORT] [--index INDEX]
                            directory

Upload the given directory into the catalog. Files will be copied or moved,
default is just to copy.

positional arguments:
  directory             Full path of directory to upload.

optional arguments:
  -h, --help            show this help message and exit
  --recursive, -r       Recurse into subdirectories. Defaults to FALSE
  --dropbox             Also create the dropbox copy. Defaults to FALSE
  --nas_root NAS_ROOT   Use this as catalog root on NAS
  --dropbox_root DROPBOX_ROOT
                        Use this as catalog root on Dropbox
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic to use. Defauls to catalog
```

### Catalog Files

Using the `add_to_elastic` script, it is already possible to populate elastic with data.
Catalog all image and video files in the given directory.

```
usage: add_to_catalog.py [-h] [--recursive] [--allow_duplicates] [--host HOST]
                         [--port PORT] [--index INDEX]
                         dirname

positional arguments:
  dirname               name of directory to catalog

optional arguments:
  -h, --help            show this help message and exit
  --recursive, -r       recurse into subdirectories. Default: false
  --allow_duplicates, -d
                        Duplicates are not ok by default.
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic. Defauls to catalog
```

### Sync Catalog with Disk
This tool will sync the catalog with the disk contents. The disk is taken as
truth, the catalog is changed based on what is on disk. New data on disk will
NOT be loaded into the catalog, use add_to_catalog for this. Items in the
catalog that are not on disk anymore are removed from the catalog. Items that
changed on disk are updated in the catalog (change in size, modify time..)

```
usage: sync_catalog_with_disk.py [-h] [--host HOST] [--port PORT]
                                 [--index INDEX] [--quiet]
                                 [dirname]

positional arguments:
  dirname        name of directory to look at

optional arguments:
  -h, --help     show this help message and exit
  --host HOST    the host where elastic runs. Default: localhost
  --port PORT    the port where elastic runs. Default: 9200
  --index INDEX  the index in elastic. Defauls to catalog
  --quiet, -q    no verbose output
```

## Utilities
These utilities are provided for testing and debugging purposes.

* List all images or video in a given directory, in JSON format `images_in_directory`
* List all file types found in a given directory `list_all_file_types`