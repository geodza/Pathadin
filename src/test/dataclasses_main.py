from dataclasses import Field, dataclass


@dataclass
class A:
    prop1: str = Field()

if __name__ == '__main__':
    a=A()