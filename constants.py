class Constants:
    attributes = ("name", "path", "dropbox_path", "nas_path", "size", "modified", "hash",
                  "type", "checksum", "captured", "location", "dimensions", "duration", "kind")
    date_keys = ("modified", "captured")
    image_types = {'png', 'jpg', 'jpeg', 'jpg2', 'jp2', 'heic', 'bmp', 'gif', 'orf', 'nef'}
    video_types = {'mov', 'avi', 'mp4', 'mpg', 'm4v'}

    IMAGE_KIND = 1
    VIDEO_KIND = 2

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
                "dropbox_path": {"type": "keyword"},
                "nas_path": {"type": "keyword"},
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
