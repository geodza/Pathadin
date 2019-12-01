from slide_viewer.ui.odict.odict import ODict3

if __name__ == '__main__':
    print(ODict3.predefined_attr)
    o3 = ODict3()
    o3[ODict3.predefined_attr] = 'predefined_attr_value'
    o3['dynamic_attr'] = '123'
    print(o3.keys())
    print(o3)
    print(dict(o3))
    del o3['dynamic_attr']
    print(o3)
    del o3.predefined_attr
    print(o3)
