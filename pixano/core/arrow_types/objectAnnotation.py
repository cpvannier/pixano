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

from typing import Optional

import pyarrow as pa

from .bbox import BBox, BBoxType
from .pose import Pose, PoseType
from .compressedRLE import CompressedRLE, CompressedRLEType

# ------------------------------------------------
#             Python type
# ------------------------------------------------


class ObjectAnnotation:
    """ObjectAnnotation type using all annotation data

    Attributes:
        id (str): Annotation unique ID
        view_id (str, optional): View ID (e.g. 'image', 'cam_2')
        bbox (list[float], optional): Bounding box coordinates in xywh format (using top left point as reference)
        bbox_source (str, optional): Bounding box source
        bbox_confidence (float, optional): Bounding box confidence
        is_group_of (bool, optional): is_group_of
        is_difficult (bool, optional): is_difficult
        is_truncated (bool, optional): is_truncated
        mask (dict[str, bytes], optional): Mask
        mask_source (str, optional): Mask source
        area (float, optional): area
        pose (dict[str, list[float]], optional): Pose
        category_id (int, optional): Category ID
        category_name (str, optional): Category name
        identity (str, optional): Identity
    """

    def __init__(
        self,
        id: str,
        view_id: Optional[str] = None,
        bbox: Optional[BBox] = [0] * 4,
        bbox_source: Optional[str] = None,
        bbox_confidence: Optional[float] = None,
        is_group_of: Optional[bool] = None,
        is_difficult: Optional[bool] = None,
        is_truncated: Optional[bool] = None,
        mask: Optional[CompressedRLE] = None,
        mask_source: Optional[str] = None,
        area: Optional[float] = None,
        pose: Optional[Pose] = {
            "cam_R_m2c": [0] * 9,
            "cam_t_m2c": [0] * 3,
        },
        category_id: Optional[int] = None,
        category_name: Optional[str] = None,
        identity: Optional[str] = None,
    ) -> None:
        self.id = id
        self.view_id = view_id
        self.bbox = bbox
        self.bbox_source = bbox_source
        self.bbox_confidence = bbox_confidence
        self.is_group_of = is_group_of
        self.is_difficult = is_difficult
        self.is_truncated = is_truncated
        self.mask = mask
        self.mask_source = mask_source
        self.area = area
        self.pose = pose
        self.category_id = category_id
        self.category_name = category_name
        self.identity = identity

    def to_dict(self) -> dict:
        """Converts the ObjectAnnotation instance to a dictionary."""
        annotation_dict = {
            "id": self.id,
            "view_id": self.view_id,
            "bbox": self.bbox.to_dict(),
            "bbox_source": self.bbox_source,
            "bbox_confidence": self.bbox_confidence,
            "is_group_of": self.is_group_of,
            "is_difficult": self.is_difficult,
            "is_truncated": self.is_truncated,
            "mask": self.mask.to_dict(),
            "mask_source": self.mask_source,
            "area": self.area,
            "pose": self.pose.to_dict(),
            "category_id": self.category_id,
            "category_name": self.category_name,
            "identity": self.identity,
        }
        return annotation_dict


# ------------------------------------------------
#             Py arrow integration
# ------------------------------------------------


class ObjectAnnotationType(pa.ExtensionType):
    """ObjectAnnotationType type as PyArrow binary"""

    def __init__(self):
        super(ObjectAnnotationType, self).__init__(
            pa.struct(
                [
                    pa.field("id", pa.string()),
                    pa.field("view_id", pa.string(), nullable=True),
                    pa.field("bbox", BBoxType(), nullable=True),
                    pa.field("bbox_source", pa.string(), nullable=True),
                    pa.field("bbox_confidence", pa.float32(), nullable=True),
                    pa.field("is_group_of", pa.bool_(), nullable=True),
                    pa.field("is_difficult", pa.bool_(), nullable=True),
                    pa.field("is_truncated", pa.bool_(), nullable=True),
                    pa.field("mask", CompressedRLEType(), nullable=True),
                    pa.field("mask_source", pa.string(), nullable=True),
                    pa.field("area", pa.float32(), nullable=True),
                    pa.field("pose", PoseType(), nullable=True),
                    pa.field("category_id", pa.int32(), nullable=True),
                    pa.field("category_name", pa.string(), nullable=True),
                    pa.field("identity", pa.string(), nullable=True),
                ]
            ),
            "ObjectAnnotation",
        )

    @classmethod
    def __arrow_ext_deserialize__(cls, storage_type, serialized):
        return ObjectAnnotationType()

    def __arrow_ext_serialize__(self):
        return b""

    def __arrow_ext_scalar_class__(self):
        return ObjectAnnotationTypeScalar

    def __arrow_ext_class__(self):
        return ObjectAnnotationArray


class ObjectAnnotationTypeScalar(pa.ExtensionScalar):
    def as_py(self) -> ObjectAnnotation:
        return ObjectAnnotation(
            self.value["id"].as_py(),
            self.value["view_id"].as_py(),
            self.value["bbox"].as_py(),
            self.value["bbox_source"].as_py(),
            self.value["bbox_confidence"].as_py(),
            self.value["is_group_of"].as_py(),
            self.value["is_difficult"].as_py(),
            self.value["is_truncated"].as_py(),
            self.value["mask"].as_py(),
            self.value["mask_source"].as_py(),
            self.value["area"].as_py(),
            self.value["pose"].as_py(),
            self.value["category_id"].as_py(),
            self.value["category_name"].as_py(),
            self.value["identity"].as_py(),
        )


class ObjectAnnotationArray(pa.ExtensionArray):
    """Class to use pa.array for ObjectAnnotationType instance"""

    @staticmethod
    def from_list_to_dict(annotation_list:list[ObjectAnnotation]) -> dict:
        """Tool function to trasnform list of ObjAnn to theirs correspondings dicts

        Args:
            annotation_list (list[ObjectAnnotation]): _description_

        Returns:
            dict: _description_
        """
        
        type_mapping = {
            BBox: BBoxType(),
            Pose: PoseType(),
            CompressedRLE: CompressedRLEType(),
            ObjectAnnotation: ObjectAnnotationType()
        }

        result_dict = {}

        if len(annotation_list) == 0:
            return result_dict

        attributes = annotation_list[0].__dict__.keys()

        for attr in attributes:
            attr_values = [getattr(annotation, attr) for annotation in annotation_list]

            if isinstance(attr_values[0], tuple(type_mapping.keys())):
                attr_type = type_mapping[type(attr_values[0])]
                attr_values = pa.array([value.to_dict() for value in attr_values], type=attr_type)


            result_dict[attr] = pa.array(attr_values)

        return result_dict
    
    @classmethod
    def from_list(cls, annotation_list: list[ObjectAnnotation]):
        attributes_dict = ObjectAnnotationArray.from_list_to_dict(annotation_list)
        return pa.StructArray.from_arrays(list(attributes_dict.values()),names= list(attributes_dict.keys()))




def is_objectAnnotation_type(t: pa.DataType) -> bool:
    return isinstance(t, ObjectAnnotationType)
