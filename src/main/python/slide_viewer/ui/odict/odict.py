import json
from collections import OrderedDict, UserDict
from enum import Enum

class ODictAttr(Enum):
    odict_display_attrs = 1
    odict_decoration_attr = 2
    odict_background_attr = 3
    odict_hidden_attrs = 4
    odict_checked_attr = 5

class ODict(UserDict):

    def __init__(self, initial_data) -> None:
        super().__init__()
        self.data = OrderedDict(initial_data)


class ODict2(OrderedDict):

    def __init__(self, initial_data) -> None:
        super().__init__(initial_data)
        for attr in ODictAttr:
            self.setdefault(attr.name)

if __name__ == '__main__':
    d = ODict({1: 1, 2: 2})
    print(d)
    od = ODict(OrderedDict({1: 1, 2: 2}))
    print(od)
    od2 = ODict(OrderedDict())
    print(od2)
    od3 = ODict(OrderedDict([(1, 1)]))
    print(od3)

    od4 = ODict2([(1, 1)])
    print(od4)
    print(od4.odict_display_attrs)

    # s1 = json.dumps(od)
    # print(s1)
    s4 = json.dumps(od4)
    print(s4)
