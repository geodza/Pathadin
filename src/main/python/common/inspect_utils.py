import inspect


def get_default_args(func):
    # https://stackoverflow.com/questions/12627118/get-a-function-arguments-default-value
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def get_default_arg(func, attr: str):
    signature = inspect.signature(func)
    param = signature.parameters[attr]
    return param.default