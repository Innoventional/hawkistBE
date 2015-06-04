import StringIO
from PIL import Image, ExifTags


def make_thumbnail(image):
    stream = StringIO.StringIO(image)
    image = Image.open(stream)

    thumbnail_size = 256, 256
    thumbnail_stream = StringIO.StringIO()

    image.thumbnail(thumbnail_size, Image.ANTIALIAS)
    image.save(thumbnail_stream, format='JPEG')
    thumbnail = thumbnail_stream.getvalue()

    return thumbnail
