import typing

from dataclasses import fields

T = typing.TypeVar('T')

# dataclass = lambda x: x
# class Meta(type):
#     def __new__(cls, name, bases, dct):
#         x = super().__new__(cls, name, bases, dct)
#         prop = ODictProp()
#         prop.name = 'max_iter'
#         setattr(x, 'max_iter', prop)
#         return x


def modify_dataclass_(cls: T):
    for f in fields(cls):
        setattr(cls, f.name, f.name)
    pass


def dataclass_fields(cls: T) -> T:
    # def __get__(self, instance, owner):
    #     if instance is not None:
    #         return instance.get(self.name, self.default_value)
    #     else:
    #         return self.name
    modify_dataclass_(cls)

    return typing.cast(T, cls)


def narrow(named_tuple: typing.NamedTuple, to_type: typing.NamedTuple):
    narrowed_named_tuple = to_type._make(
        [getattr(named_tuple, field) for field in named_tuple._fields if field in to_type._fields])
    return narrowed_named_tuple