class Constants:
    attributes = ("name", "path", "dropbox_path", "catalog", "size", "modified", "hash",
                  "type", "checksum", "captured", "location", "dimensions", "duration", "kind")
    leave_out_when_reading_from_elastic = ("name", "path", "type", "hash", "kind", "meta")     # these are set automatically
    date_keys = ("modified", "captured")
    image_types = {'png', 'jpg', 'jpeg', 'jpg2', 'jp2', 'heic', 'bmp', 'gif', 'orf', 'nef'}
    video_types = {'mov', 'avi', 'mp4', 'mpg', 'm4v'}
    other_types = {'psd'}

    IMAGE_KIND = 1
    VIDEO_KIND = 2
    OTHER_KIND = 3

    index = {
        "mappings": {
            "properties": {
                "name": {"type": "text",
                         "fields": {
                             "keyword": {
                                 "type": "keyword",
                                 "ignore_above": 256
                             }
                         }},
                "path": {"type": "text",
                         "fields": {
                             "keyword": {
                                 "type": "keyword",
                                 "ignore_above": 256
                             }
                         }},
                "dropbox_path": {"type": "boolean"},
                "catalog": {"type": "boolean"},
                "size": {"type": "integer"},
                "duration": {"type": "integer"},
                "captured": {"type": "date"},
                "modified": {"type": "date"},
                "kind": {"type": "keyword"},
                "type": {"type": "keyword"},
                "hash": {"type": "keyword"},
                "dimensions": {"type": "keyword"},
                "checksum": {"type": "keyword"},
                "location": {"type": "geo_point"}
            }
        }
    }

    catalog_root: str = "ImageCatalog"
    nas_mount: str = "/Volumes/Photos"

    exif_date_time_original: str = "EXIF DateTimeOriginal"
    exif_width: str = "EXIF ExifImageWidth"
    exif_height: str = "EXIF ExifImageLength"
    exif_date_time_format: str = "%Y:%m:%d %H:%M:%S"
    video_duration_format: str = "%Y-%m-%d %H:%M:%S"
    GPS: dict = dict(latR="GPS GPSLatitudeRef",
                     lat="GPS GPSLatitude",
                     lonR="GPS GPSLongitudeRef",
                     lon="GPS GPSLongitude"
                     )
