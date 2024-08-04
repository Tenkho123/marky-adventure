from kivy.uix.widget import Widget
from kivy.uix.image import Image

from kivy.properties import NumericProperty, ObjectProperty, ListProperty

from kivy.clock import Clock

from kivy.core.window import Window

class Down_left_way(Widget):
    GAP_SIZE_RATIO = NumericProperty(1)
    BORDER_SIZE_RATIO = NumericProperty(1)
    default_width = NumericProperty(1)
    root_width = NumericProperty(1)
    
    vertical_border_texture = ObjectProperty(None)
    horizontal_border_texture = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vertical_border_texture = Image(source = "assets/vertical_border.png").texture
        self.vertical_border_texture.wrap = "repeat"
        
        self.horizontal_border_texture = Image(source = "assets/horizontal_border.png").texture
        self.horizontal_border_texture.wrap = "repeat"

        
    def on_gap_size(self, *args):
        Clock.schedule_once(self.on_size, 0)