from kivy.uix.widget import Widget
from kivy.uix.image import Image

from kivy.properties import NumericProperty, ObjectProperty, ListProperty

from kivy.clock import Clock

from kivy.core.window import Window

class Horizontal_way(Widget):
    GAP_SIZE_RATIO = NumericProperty(1)
    BORDER_SIZE_RATIO = NumericProperty(1)
    border_texture = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_texture = Image(source = "assets/horizontal_border.png").texture
        self.border_texture.wrap = "repeat"
    
    def on_gap_size(self, *args):
        Clock.schedule_once(self.on_size, 0)