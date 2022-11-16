from typing import Dict, List

import pandas as pd
from base import ClarifaiDataset
from clarifai_grpc.grpc.api import resources_pb2
from google.protobuf.struct_pb2 import Struct
from tqdm import tqdm
from utils import create_image_df


class ImageClassificationDataset(ClarifaiDataset):
  """
  Load image classification data from csv file.
  The csv must have only two columns, the image path `image_path`
  and the `label` columns.
  """

  def __init__(self, csv_file_path: str, dataset_id: str, split: str) -> None:
    super().__init__(csv_file_path, dataset_id, split)
    self.image_df = pd.read_csv(self.csv_file_path)

  def __len__(self):
    return len(self._all_input_protos)

  def create_input_protos(self,
                          image_path: str,
                          label: str,
                          input_id: str,
                          dataset_id: str,
                          metadata: Dict,
                          use_urls=False,
                          allow_dups=False):
    """
    Create input protos for each image, label input pair.
    Args:
    	`image_path`: full image path or valid url
    		ending with an image extension.
    	`label`: image label
    	`input_id: unique input id
    	`dataset_id`: Clarifai dataset id
    	`metadata`: image metadata
    	`use_urls`: If set to True it means all image_paths are provided as urls and
    		hence uploading will attempt to read images from urls.
    		The default behavior is reading images from local storage.
    	`allow_dups`: Boolean indicating whether to allow duplicate url inputs
    Returns:
    	An input proto representing a single row input
    """
    if use_urls is False:
      input_proto = resources_pb2.Input(
          id=input_id,
          dataset_ids=[dataset_id],
          data=resources_pb2.Data(
              image=resources_pb2.Image(base64=open(image_path, 'rb').read(),),
              concepts=[
                  resources_pb2.Concept(id=label, name=label, value=1.),
              ],
              metadata=metadata))
    else:
      input_proto = resources_pb2.Input(
          id=input_id,
          dataset_ids=[dataset_id],
          data=resources_pb2.Data(
              image=resources_pb2.Image(
                  url=image_path,  # image_path here maps to a valid url
                  allow_duplicate_url=allow_dups),
              concepts=[
                  resources_pb2.Concept(id=label, name=label, value=1.),
              ],
              metadata=metadata))

    return input_proto

  def _get_input_protos(self) -> List:
    """
    Creates input image protos for each row of the dataframe.
    Returns:
    	A list of input protos
    """
    for i, row in tqdm(self.image_df.iterrows(), desc="Loading images"):
      metadata = Struct()
      image_path = row["image_path"]
      label = row["label"]  # clarifai concept
      input_id = f"{self.split}-{str(i)}"
      metadata.update({"label": label, "split": self.split})

      input_proto = self.create_input_protos(image_path, label, input_id, self.dataset_id,
                                             metadata)

      self._all_input_protos.append(input_proto)

    return iter(self._all_input_protos)


class TextClassificationDataset(ClarifaiDataset):
  """
  Upload text classification datasets to clarifai datasets
  """

  def __init__(self, csv_file_path: str, dataset_id: str, split: str) -> None:
    super().__init__(csv_file_path, dataset_id, split)
    self.image_df = pd.read_csv(self.csv_file_path)

  def __len__(self):
    return len(self._all_input_protos)

  def create_input_protos(self, text_input: str, label: List, input_id: str, dataset_id: str,
                          metadata: Dict):
    """
    Create input protos for each text, label input pair.
    Args:
    	`text_input`: text string.
    	`label`: image label
    	`input_id: unique input id
    	`dataset_id`: Clarifai dataset id
    	`metadata`: image metadata
    Returns:
    	An input proto representing a single row input
    """
    input_proto = resources_pb2.Input(
        id=input_id,
        dataset_ids=[dataset_id],
        data=resources_pb2.Data(
            text=resources_pb2.Text(raw=text_input),
            concepts=[
                resources_pb2.Concept(id=_label, name=_label, value=1.) for _label in set(label)
            ],
            metadata=metadata))

    return input_proto

  def _get_input_protos(self) -> List:
    """
    Creates input protos for each row of the dataframe.
    Returns:
    	A list of input protos
    """
    for i, row in tqdm(self.image_df.iterrows(), desc="Loading Text"):
      metadata = Struct()
      text = row["text"]
      label = list(row["label"])  # clarifai concept
      input_id = f"{self.split}-{str(i)}"
      metadata.update({"label": label, "split": self.split})

      input_proto = self.create_input_protos(text, label, input_id, self.dataset_id, metadata)

      self._all_input_protos.append(input_proto)

    return iter(self._all_input_protos)


class VisualDetectionDataset(ClarifaiDataset):
  """
  Visual detection dataset upload class.
  """

  def __init__(self, file_path, label_path, dataset_id, split,
               labels_from_text_file=False) -> None:
    super().__init__(None, dataset_id, split)
    self.file_path = file_path
    self.label_path = label_path
    self.image_df = create_image_df(
        self.file_path, self.label_path, from_text_file=labels_from_text_file)
    self._annotations = []

  def create_input_protos(self, image_path: str, label: List, input_id: str, dataset_id: str,
                          metadata: Dict):
    """
    Create input protos for each image, label input pair.
    Args:
    	`image_path`: absolute image file path
    	`label`: image label
    	`input_id: unique input id
    	`dataset_id`: Clarifai dataset id
    	`metadata`: image metadata
    Returns:
    	An input proto representing a single row input
    """
    input_image_proto = resources_pb2.Input(
        id=input_id,
        dataset_ids=[dataset_id],
        data=resources_pb2.Data(
            image=resources_pb2.Image(base64=open(image_path, 'rb').read(),),
            concepts=[
                resources_pb2.Concept(id=_label, name=_label, value=1.) for _label in set(label)
            ],
            metadata=metadata))

    return input_image_proto

  def create_annotation_protos(self, label: str, annotations: List, input_id: str, dataset_id: str,
                               metadata: Dict):
    """
    Create input protos for each image, label input pair.
    Args:
    	`image_path`: absolute image file path
    	`label`: image label
    	`input_id: unique input id
    	`dataset_id`: Clarifai dataset id
    	`metadata`: image metadata
    Returns:
    	An input proto representing a single row input
    """
    input_annot_proto = resources_pb2.Annotation(
        input_id=input_id,
        data=resources_pb2.Data(regions=[
            resources_pb2.Region(
                region_info=resources_pb2.RegionInfo(bounding_box=resources_pb2.BoundingBox(
                    # Annotations ordering: [xmin, ymin, xmax, ymax]
                    # top_row must be less than bottom row
                    # left_col must be less than right col
                    top_row=annotations[1],  #y_min
                    left_col=annotations[0],  #x_min
                    bottom_row=annotations[3],  #y_max
                    right_col=annotations[2]  #x_max
                )),
                data=resources_pb2.Data(concepts=[resources_pb2.Concept(id=label, value=1.)]))
        ]))

    return input_annot_proto

  def _get_input_protos(self) -> List:
    """
    Create input image protos for each row of the dataframe.
    Returns:
    	A list of input protos
    """
    for i, row in tqdm(self.image_df.iterrows(), desc="Loading images"):
      metadata = Struct()
      image = row["image"]
      label = row["label"]  # list
      bboxes = row["bboxes"]  # [xmin, ymin, xmax, ymax]
      input_id = f"{row['id']}-{str(i)}"
      metadata.update({"label": row['id'], "split": self.split})

      input_image_proto = self.create_input_protos(image, label, input_id, self.dataset_id,
                                                   metadata)
      self._all_input_protos.append(input_image_proto)

      # iter over bboxes and annotations and map to each input_id
      # one id could have more than one bbox and label
      for i in range(len(bboxes)):
        input_annot_proto = self.create_annotation_protos(label[i], bboxes[i], input_id,
                                                          self.dataset_id, metadata)
        self._annotations.append(input_annot_proto)

    return iter(self._all_input_protos), iter(self._annotations)