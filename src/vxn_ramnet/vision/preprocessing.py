from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np


def load_rgb(path: str | Path, input_size: tuple[int,int], flip: bool=False) -> np.ndarray:
    height,width=input_size
    with Image.open(path) as image:
        image=ImageOps.exif_transpose(image).convert("RGB")
        if flip: image=ImageOps.mirror(image)
        image=image.resize((width,height),Image.Resampling.BILINEAR)
        return np.asarray(image,dtype=np.float32)
