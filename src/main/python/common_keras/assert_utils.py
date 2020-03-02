import numpy as np
from keras import Model


def assert_model_input(model: Model, X: np.ndarray):
    assert len(X.shape) == len(model.input_shape)
    assert tuple(X.shape[1:]) == tuple(model.input_shape[1:])
    assert np.can_cast(X.dtype, model.input.dtype.as_numpy_dtype)


def assert_model_output(model: Model, Y: np.ndarray):
    assert len(Y.shape) == len(model.output_shape)
    assert tuple(Y.shape[1:]) == tuple(model.output_shape[1:])
    assert np.can_cast(Y.dtype, model.output.dtype.as_numpy_dtype)
