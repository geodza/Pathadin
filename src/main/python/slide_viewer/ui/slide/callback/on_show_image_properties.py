import json
from collections import OrderedDict

from slide_viewer.ui.common.dialog.text_dialog import TextDialog
from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView


def on_show_image_properties(view: GraphicsView) -> None:
    if not view.slide_helper:
        return
    props = view.slide_helper.get_properties()
    main_props = {prop: val for prop, val in props.items() if prop.startswith("openslide")}
    ordered_props = OrderedDict(main_props.items())
    ordered_props.update(props)
    main_props_text = json.dumps(main_props, indent=2)
    full_props_text = json.dumps(ordered_props, indent=2)

    props_dialog = TextDialog(full_props_text, main_props_text, True, view)
    props_dialog.show()
