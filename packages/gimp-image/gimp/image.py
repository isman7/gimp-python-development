import gi

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

gi.require_version('Gegl', '0.4')
from gi.repository import Gegl

import numpy as np


def gimp_layer_to_numpy_image(layer: Gimp.Layer) -> np.ndarray:
    layer_width = layer.width()
    layer_height = layer.height()
    layer_channels = layer.bpp()
    layer_buffer = layer.get_buffer()

    rect = Gegl.Rectangle.new(0, 0, layer_width, layer_height)
    buffer_bytes = layer_buffer.get(rect, 1.0, None, Gegl.AbyssPolicy.CLAMP)

    return np.frombuffer(buffer_bytes, dtype=np.uint8).reshape(layer_height, layer_width, layer_channels)


def numpy_image_to_gimp_layer(
        image: np.ndarray,
        gimp_image: Gimp.Image,
        layer_name: str = "New layer"
) -> Gimp.Layer:

    layer = Gimp.Layer.new(
        gimp_image,
        layer_name,
        gimp_image.width(),
        gimp_image.height(),
        Gimp.ImageBaseType.RGB,
        100,
        Gimp.LayerMode.NORMAL
    )
    layer_width = layer.width()
    layer_height = layer.height()
    layer_buffer = layer.get_buffer()

    rect = Gegl.Rectangle.new(0, 0, layer_width, layer_height)
    buffer_bytes = np.uint8(image).tobytes()

    layer_buffer.set(rect, "RGB u8", buffer_bytes)

    return layer


def numpy_image_to_gimp_image(image: np.ndarray) -> Gimp.Image:
    height, width, channels = image.shape

    gimp_image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)
    layer = numpy_image_to_gimp_layer(image, gimp_image, "Layer 1")

    gimp_image.insert_layer(layer, layer.get_parent(), 0)

    return gimp_image


def display_image(image: np.ndarray) -> Gimp.Image:
    gimp_image = numpy_image_to_gimp_image(image)
    Gimp.Display.new(gimp_image)

    return gimp_image
