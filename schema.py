"""  python 模組文件名 : schema.py

schema.py 定義了 laptop_infers.json的資料結構

"""  


from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Labels(BaseModel):
    """
    The `Labels` class represents a set of bounding boxes and corresponding scores for object detection.

    """

    # We use float instead of int here to match the output of Faster R-CNN model
    boxes: List[List[float]] = Field(..., example=[[0, 0, 0, 0]], title="boxes")
    scores: List[float] = Field(..., example=[0.3], title="scores")


class InferenceResult(BaseModel):
    """
    The `InferenceResult` class represents the result of an inference process, including information
    about whether there is a defect, the score of the inference, and the labels associated with the
    inference.
    """

    defect: bool = Field(..., example=True, title="defect")
    score: float = Field(..., example=0.3, ge=-999, title="score")
    labels: Dict[str, Labels] = Field(
        ...,
        example={"Top_00": {"boxes": [[0, 0, 0, 0]], "scores": [0.3]}},
        title="labels",
    )


class ModelParams(BaseModel):
    """
    The `ModelParams` class defines the output values for model inference, including the model key, mask
    key, score threshold, and box size threshold.
    """

    model_key: str = Field(..., example="G9A", title="model key")
    mask_key: str = Field(..., example="G9A", title="mask key")
    score_thr: float = Field(..., example=0.0, ge=-10, title="score threshold")
    box_size_thr: int = Field(..., example=1000, ge=0, title="box size threshold")

    # Check https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.protected_namespaces
    model_config = ConfigDict(protected_namespaces=())


class LaptopInfers(BaseModel):
    """
    The `LaptopInfers` class represents the inference results of a laptop model, including the
    timestamp, version, status, model parameters, and inference results.
    """

    timestamp: str = Field(..., example="2021-01-01_00-00-00", title="timestamp")
    version: str = Field(..., example="v1.0.0", title="version")
    status: str = Field(..., example="success", title="status")
    params: ModelParams = ...
    results: Optional[InferenceResult] = None


class InferenceOutput(BaseModel):
    """
    The `InferenceOutput` class represents the output of an inference process for a laptop, including
    the laptop key and a list of laptop infers.
    """

    laptop_key: str = Field(..., example="laptop_1", title="laptop key")
    laptop_infers: List[LaptopInfers] = ...


class InferenceInput(BaseModel):
    """
    The `InferenceInput` class represents the input data for an inference process, including a laptop
    key and model parameters.
    """

    laptop_key: str = Field(..., example="laptop_1", title="laptop key")
    params: ModelParams = ...
