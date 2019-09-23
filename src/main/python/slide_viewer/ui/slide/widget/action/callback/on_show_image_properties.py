import json
from collections import OrderedDict

from slide_viewer.ui.common.text_dialog import TextDialog
from slide_viewer.ui.slide.widget.slide_viewer_widget import SlideViewerWidget


def on_show_image_properties(widget: SlideViewerWidget):
    if not widget.slide_helper:
        return
    props = widget.slide_helper.get_properties()
    main_props = {prop: val for prop, val in props.items() if prop.startswith("openslide")}
    ordered_props = OrderedDict(main_props.items())
    ordered_props.update(props)
    main_props_text = json.dumps(main_props, indent=2)
    full_props_text = json.dumps(ordered_props, indent=2)

    props_dialog = TextDialog(full_props_text, main_props_text, True, widget)
    props_dialog.show()
