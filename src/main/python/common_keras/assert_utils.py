import numpy as np
from keras import Model


def assert_model_input(model: Model, X: np.ndarray):
    assert len(X.shape) == len(model.input_shape)
    assert tuple(X.shape[1:]) == tuple(model.input_shape[1:])
    assert np.can_cast(X.dtype, model.input.dtype.as_numpy_dtype, casting='same_kind')


def assert_model_output(model: Model, Y: np.ndarray):
    assert len(Y.shape) == len(model.output_shape)
    assert tuple(Y.shape[1:]) == tuple(model.output_shape[1:])
    assert np.can_cast(Y.dtype, model.output.dtype.as_numpy_dtype, casting='same_kind')

if __name__ == '__main__':
    print(np.can_cast(np.int, np.float32))
    print(np.can_cast(np.float32, np.int))
    print(np.can_cast(np.float32, np.float64))
    print(np.can_cast(np.float64, np.float32))
    print(np.can_cast(np.float64, np.float))
    print(np.can_cast(np.float64, float))
    print(np.can_cast(np.float32, float))
    print(np.can_cast(np.uint8, float))
