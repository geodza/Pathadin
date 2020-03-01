import numpy as np
from keras import Model


def assert_model_input(model: Model, X: np.ndarray):
    assert len(X.shape) == len(model.input_shape)
    assert X.shape[1:] == model.input_shape[1:]
    assert X.dtype == model.input.dtype.as_numpy_dtype


def assert_model_output(model: Model, Y: np.ndarray):
    assert len(Y.shape) == len(model.output_shape)
    assert Y.shape[1:] == model.output_shape[1:]
    assert Y.dtype == model.output.dtype.as_numpy_dtype
