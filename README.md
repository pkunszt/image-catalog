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

## Catalog Main Executables
Several local executables are available to perform all cataloguing work.
* Uplopad local files to catalog: `upload_to_nas_from_disk`  : upload images and videos to the NAS catalog location, 
optionally also to dropbox, naming is based on creation time and location. 
This is to upload data from local disk to the NAS.
* Upload dropbox files to catalog: `upload_to_dropbox_from_dropbox` : when the images/videos are already on
dropbox, upload it into the dropbox catalog. The syncronization to NAS can be done later, see below
* Synchronize between NAS and Dropbox: `sync_dropbox_to_nas` and `sync_nas_to_dropbox`, this makes sure
that all catalog items are on both locations
* Sometimes we have a directory that we uploaded and we do not want to keep the local files anymore.
But we may have made changes. So just remove the files that are already in the catalog and keep only
those that are not in the catalog yet, `delete_from_directory_if_in_catalog` will do that. Works on both file or dropbox directories.

## Executable Tools in the tools directory
* Import old catalog to new one (one timer, this is only useful to me): `import_old_catalog` will do the import,
`check_old_catalog_structure` will report problems with the structure if any
* Delete IDs from catalog, this is useful if we have some errors to fix: `delete_ids`
* List all images in a directory, to check: `images_in_directory`

### Upload Files to Catalog: Local disk to local NAS
This script will upload the files in a given directory into the catalog. The files
will not be removed unless explicitly asked to do so using the move flag.
The files can be also copied to dropbox in one go, but that is really slow so
do it only for very few files.
```
usage: upload_to_nas_from_disk.py [-h] [--recursive] [--move] [--quiet]
                                  [--dryrun] [--dropbox] [--nas_root NAS_ROOT]
                                  [--dropbox_root DROPBOX_ROOT] [--host HOST]
                                  [--port PORT] [--index INDEX]
                                  directory

Upload the given directory into the catalog. Files will be copied into place
on the NAS. The files will also be uploaded to the dropbox copy if explicitly
requested with --dropbox. The sync can be performed also later using
sync_nas_to_dropbox.

positional arguments:
  directory             Full path of directory to upload.

optional arguments:
  -h, --help            show this help message and exit
  --recursive, -r       Recurse into subdirectories. Defaults to FALSE
  --move, -m            Move the files, don't just copy them
  --quiet, -q           Recurse into subdirectories. Defaults to FALSE
  --dryrun, -d          Do a dry run only, print what would be done. Defaults
                        to FALSE
  --dropbox             Also create the dropbox copy. Defaults to FALSE
  --nas_root NAS_ROOT   Use this as catalog root on NAS
  --dropbox_root DROPBOX_ROOT
                        Use this as catalog root on Dropbox
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic to use. Defauls to catalog
```

### Upload Files to Catalog: Dropbox folder to Dropbox Catalog

If we have a folder with images and videos already on dropbox, we can add them to the catalog
right there. This happens with the camera roll all the time. Again a NAS copy can be requested
right here using the nas flag. A limit is also available to process only a limited amount
of files in a given directory, this is useful if the image directories contain thousands of entries.
```
usage: upload_to_dropbox_from_dropbox.py [-h] [--recursive] [--move] [--quiet]
                                         [--dryrun] [--nas] [--limit LIMIT]
                                         [--nas_root NAS_ROOT]
                                         [--dropbox_root DROPBOX_ROOT]
                                         [--host HOST] [--port PORT]
                                         [--index INDEX]
                                         directory

Load the given dropbox path into the catalog. The dropbox catalog will be
used, meaning that all files in the dropbox directory will be copied to the
catalog location on dropbox. It is a dropbox-to-dropbox copy operation. Files
are downloaded to the NAS copy of the catalog only if explicitly requested
using the --nas flag. The nas catalog can be syncronized also later using the
sync_dropbox_to_nas tool.

positional arguments:
  directory             Full path of dropbox directory to load.

optional arguments:
  -h, --help            show this help message and exit
  --recursive, -r       Recurse into subdirectories. Defaults to FALSE
  --move, -m            Move the files, don't just copy them
  --quiet, -q           Recurse into subdirectories. Defaults to FALSE
  --dryrun, -d          Do a dry run only, print what would be done. Defaults
                        to FALSE
  --nas                 Also create the NAS copy. Defaults to FALSE
  --limit LIMIT, -l LIMIT
                        Limit the number of files processed
  --nas_root NAS_ROOT   Use this as catalog root on NAS
  --dropbox_root DROPBOX_ROOT
                        Use this as catalog root on Dropbox
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic to use. Defauls to catalog
```


### Synchronize between NAS and dropbox, both ways
There are two dedicated scripts for that.
```
usage: sync_nas_to_dropbox.py [-h] [--limit LIMIT] [--verbose]
                              [--nas_root NAS_ROOT]
                              [--dropbox_root DROPBOX_ROOT] [--host HOST]
                              [--port PORT] [--index INDEX]

Scan the catalog for entries where the NAS copy is there but the dropbox copy
is not yet available.

optional arguments:
  -h, --help            show this help message and exit
  --limit LIMIT, -l LIMIT
                        Just do it for so many files
  --verbose, -v         Verbose output, print each file name copied
  --nas_root NAS_ROOT   Use this as catalog root on NAS
  --dropbox_root DROPBOX_ROOT
                        Use this as catalog root on Dropbox
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic to use. Defauls to catalog

```

From dropbox to nas
```
usage: sync_dropbox_to_nas.py [-h] [--limit LIMIT] [--verbose]
                              [--nas_root NAS_ROOT]
                              [--dropbox_root DROPBOX_ROOT] [--host HOST]
                              [--port PORT] [--index INDEX]

Scan the catalog for entries where the dropbox copy is there but the NAS copy
is not yet available.

optional arguments:
  -h, --help            show this help message and exit
  --limit LIMIT, -l LIMIT
                        Just do it for so many files
  --verbose, -v         Verbose output, print each file name copied
  --nas_root NAS_ROOT   Use this as catalog root on NAS
  --dropbox_root DROPBOX_ROOT
                        Use this as catalog root on Dropbox
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic to use. Defauls to catalog
```

### Sync NAS catalog with its own disk contents
It can happen on the NAS that the local disk data is modified manually, especially
moved to a new location or deleted.
The disk is scanned and checked against the catalog content. Automated action is taken
or the user is asked what to do if unclear.

```
usage: sync_catalog_with_disk.py [-h] [--quiet] [--recursive]
                                 [--nas_root NAS_ROOT]
                                 [--dropbox_root DROPBOX_ROOT] [--host HOST]
                                 [--port PORT] [--index INDEX]
                                 dirname

This tool will sync the catalog with the disk contents. The disk is taken as
truth, the catalog is changed based on what is on disk. New data on disk will
be loaded into the catalog. Items in the catalog that are not on disk anymore
are removed from the catalog, if they were moved, that will be detected. Items
that changed on disk with the same name are not detected. (change in size,
modify time..)

positional arguments:
  dirname               name of directory to look at

optional arguments:
  -h, --help            show this help message and exit
  --quiet, -q           no verbose output
  --recursive, -r       no verbose output
  --nas_root NAS_ROOT   Use this as catalog root on NAS
  --dropbox_root DROPBOX_ROOT
                        Use this as catalog root on Dropbox
  --host HOST           the host where elastic runs. Default: localhost
  --port PORT           the port where elastic runs. Default: 9200
  --index INDEX         the index in elastic to use. Defauls to catalog
```


## Utilities
These utilities are provided for testing and debugging purposes.

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

* List all images or video in a given directory, in JSON format `images_in_directory`
* List all file types found in a given directory `list_all_file_types`
