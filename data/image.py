from data.entry import Entry


class InvalidImageError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Image(Entry):
    """This is the image entry in the catalog."""

    __image_types = {'png', 'jpg', 'jpeg', 'jpg2', 'jp2', 'heic', 'bmp', 'gif', 'orf', 'nef'}

    def __init__(self):
        self.id = 0

    @property
    def kind(self):
        """Image kind is 0 by definition"""
        return 0

    @Entry.name.setter
    def name(self, name):
        super(Image, self.__class__).name.fset(self, name)   # This is how to call a superclass setter
        if self.type not in self.__image_types:
            raise InvalidImageError(f"Not an image with extension {self.type}")

    def to_dict(self):
        return dict(
            name=self.name,
            path=self.path,
            size=self.size,
            created=self.date,
            type=self.type,
            kind=self.kind,
            hash=self.hash,
            checksum=self.checksum
        )