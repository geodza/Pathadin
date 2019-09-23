from slide_viewer.ui.slide.graphics.slide_graphics_grid_item import SlideGraphicsGridItem


def on_grid_toggle(grid_item: SlideGraphicsGridItem):
    if grid_item:
        is_visible = grid_item.isVisible()
        grid_item.setVisible(not is_visible)
