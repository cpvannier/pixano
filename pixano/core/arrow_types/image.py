# @Copyright: CEA-LIST/DIASI/SIALV/LVA (2023)
# @Author: CEA-LIST/DIASI/SIALV/LVA <pixano@cea.fr>
# @License: CECILL-C
#
# This software is a collaborative computer program whose purpose is to
# generate and explore labeled data for computer vision applications.
# This software is governed by the CeCILL-C license under French law and
# abiding by the rules of distribution of free software. You can use,
# modify and/ or redistribute the software under the terms of the CeCILL-C
# license as circulated by CEA, CNRS and INRIA at the following URL
#
# http://www.cecill.info

import base64
from typing import IO

import pyarrow as pa
from etils import epath


class Image:
    """Image type using URI or bytes

    Attributes:
        _uri (str): Image URI
        _bytes (bytes): Image bytes
        _preview_bytes (bytes): Image preview bytes
        uri_prefix (epath.PathLike, optional): Image URI prefix. Defaults to None.
    """

    def __init__(
        self,
        uri: str,
        bytes: bytes,
        preview_bytes: bytes,
        uri_prefix: epath.PathLike = None,
    ):
        """Initialize image from URI or bytes

        Args:
            uri (str): Image URI
            bytes (bytes): Image bytes
            preview_bytes (bytes): Image preview bytes
            uri_prefix (epath.PathLike, optional): Image URI prefix. Defaults to None.
        """
        self._uri = uri
        self._bytes = bytes
        self._preview_bytes = preview_bytes

        self.uri_prefix = uri_prefix

    @property
    def bytes(self) -> bytes:
        """Return image bytes

        Returns:
            bytes: Image bytes
        """

        if self._bytes is not None:
            return self._bytes
        elif self._uri is not None:
            with self.open() as f:
                return f.read()
        else:
            return None

    @property
    def preview_url(self) -> str:
        """Return image preview URL

        Returns:
            str: Image preview URL
        """

        encoded = base64.b64encode(self._preview_bytes).decode("utf-8")
        url = f"data:image;base64,{encoded}"
        return url

    @property
    def url(self) -> str:
        """Return image URL

        Returns:
            str: Image URL
        """

        # TODO need to check if not None
        data = self.bytes
        if data is not None:
            encoded = base64.b64encode(data).decode("utf-8")
            url = f"data:image;base64,{encoded}"
            return url
        else:
            return ""

    def open(self) -> IO:
        """Open image

        Returns:
            IO: Opened image
        """

        # TODO add prefix/auth/http/s3 ...
        if self.uri_prefix is not None:
            uri = self.uri_prefix / self._uri  # type: ignore
        else:
            uri = self._uri
        return open(uri, "rb")

    def display(self, preview=False):
        """Display image

        Args:
            preview (bool, optional): True to display image preview instead of full image. Defaults to False.

        Returns:
            IPython.core.display.Image: Image as IPython Display
        """

        from IPython.core.display import Image as IPyImage

        if preview:
            data = self._preview_bytes
        else:
            data = self._bytes

        inferred_format = IPyImage(data).format
        encoded = base64.b64encode(data).decode("utf-8")
        url = f"data:image;base64,{encoded}"
        return IPyImage(url=url, format=inferred_format)

    def to_dict(self) -> dict[str, "bytes", "bytes"]:
        """convert image attribute to dict

        Returns:
            dict: dict with image attribute
        """
        return {
            "uri": self._uri,
            "bytes": self._bytes,
            "preview_bytes": self._preview_bytes,
        }


class ImageType(pa.ExtensionType):
    """Image type as PyArrow StructType"""

    def __init__(self):
        super(ImageType, self).__init__(
            pa.struct(
                [
                    pa.field("uri", pa.utf8()),
                    pa.field("bytes", pa.binary()),
                    pa.field("preview_bytes", pa.binary()),
                ]
            ),
            "Image",
        )

    def __arrow_ext_serialize__(self):
        return b""

    @classmethod
    def __arrow_ext_deserialize__(cls, storage_type, serialized):
        return ImageType()

    def __arrow_ext_scalar_class__(self):
        return ImageScalar

    def __arrow_ext_class__(self):
        return ImageArray


class ImageScalar(pa.ExtensionScalar):
    def as_py(self) -> Image:
        return Image(
            self.value["uri"].as_py(),
            self.value["bytes"].as_py(),
            self.value["preview_bytes"].as_py(),
        )


class ImageArray(pa.ExtensionArray):
    """Class to use pa.array for Image instance"""

    @classmethod
    def from_Image_list(cls, image_list: list[Image]) -> pa.Array:
        """Create Image pa.array from image list

        Args:
            image_list (list[Bbox]): list of image

        Returns:
            pa.Array: pa.array of Image
        """
        image_dicts = [image.to_dict() for image in image_list]

        return pa.array(image_dicts, ImageType())


def is_image_type(t: pa.DataType) -> bool:
    """Returns True if value is an instance of ImageType

    Args:
        t (pa.DataType): Value to check

    Returns:
        bool: Type checking response
    """

    return isinstance(t, ImageType)
