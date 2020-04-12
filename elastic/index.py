
class Index:
    _image_default = "images"
    _video_default = "videos"

    _image_index: str
    _video_index: str

    _item_type_to_index_map: {}

    def __init__(self):
        self._image_index = Index._image_default
        self._video_index = Index._video_default
        self._item_type_to_index_map = {0: self.image, 1: self.video}

    @property
    def image(self):
        return self._image_index

    @property
    def video(self):
        return self._video_index

    @image.setter
    def image(self, img):
        self._image_index = img
        self.map[0] = img

    @video.setter
    def video(self, vid):
        self._video_index = vid
        self.map[1] = vid

    @property
    def map(self):
        return self._item_type_to_index_map

    def from_kind(self, kind):
        return self.map[kind]
