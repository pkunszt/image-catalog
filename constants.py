class Constants:
    attributes = ("name", "path", "dropbox_path", "catalog", "size", "modified", "hash",
                  "type", "checksum", "captured", "location", "dimensions", "duration", "kind")
    leave_out_when_reading_from_elastic = ("name", "path", "type", "hash", "kind", "meta")     # these are set automatically
    date_keys = ("modified", "captured")
    image_types = {'png', 'jpg', 'jpeg', 'jpg2', 'jp2', 'heic', 'bmp', 'gif', 'orf', 'nef', 'cr2', 'mpo'}
    video_types = {'mov', 'avi', 'mp4', 'mpg', 'm4v', 'wmv', 'mts', '3gp'}
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
    video_duration_format2: str = "%Y-%m-%d/ %H:%M"
    GPS: dict = dict(latR="GPS GPSLatitudeRef",
                     lat="GPS GPSLatitude",
                     lonR="GPS GPSLongitudeRef",
                     lon="GPS GPSLongitude"
                     )


class TestConstants:
    testdir = "testfiles"
    files = ["P1030250.MOV", "boarding.mov", "cartoon.png", "food.heic",
             "milky-way-nasa.jpg", "spiderman.jpg", "spidey.jpeg", "thor.jpeg", "ztest.psd"]
    sizes = [3691944, 30830885, 876273, 1643711, 9711423, 28398, 28398, 5906, 5]
    types = ["mov", "mov", "png", "heic", "jpg", "jpg", "jpeg", "jpeg", "psd"]
    kinds = [Constants.VIDEO_KIND] * 2 + [Constants.IMAGE_KIND] * 6 + [Constants.OTHER_KIND]
    duration = [11, 21]


def get_months() -> list:
    mon = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
           "October", "November", "December"]
    return [
        f"{k:02}_{v}"
        for k, v in enumerate(mon, 1)
    ]
