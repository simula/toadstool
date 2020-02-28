
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import GlobalAveragePooling2D

from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50

def build_resnet50(input_shape):

    base_model = ResNet50(
        include_top=False,
        weights="imagenet",
        input_shape=input_shape
    )

    inputs = base_model.input
    x = GlobalAveragePooling2D()(inputs)
    output = Dense(1)(x)
    model = Model(inputs=inputs, outputs=output)

    return model


    