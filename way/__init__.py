from way import vertical_way
from way import horizontal_way
from way import down_left_way
from way import down_right_way
from way import up_left_way
from way import up_right_way

from kivy.properties import NumericProperty

class Way():
    GAP_SIZE_RATIO = 5.5
    BORDER_SIZE_RATIO = 10

    
    def Vertical_way(self):
        vw = vertical_way.Vertical_way()
        vw.GAP_SIZE_RATIO = self.GAP_SIZE_RATIO
        vw.BORDER_SIZE_RATIO = self.BORDER_SIZE_RATIO
        return vw
    
    def Horizontal_way(self):
        hw = horizontal_way.Horizontal_way()
        hw.GAP_SIZE_RATIO = self.GAP_SIZE_RATIO
        hw.BORDER_SIZE_RATIO = self.BORDER_SIZE_RATIO
        return hw
    
    def Down_left_way(self):
        dlw = down_left_way.Down_left_way()
        dlw.GAP_SIZE_RATIO = self.GAP_SIZE_RATIO
        dlw.BORDER_SIZE_RATIO = self.BORDER_SIZE_RATIO
        return dlw
    
    def Down_right_way(self):
        drw = down_right_way.Down_right_way()
        drw.GAP_SIZE_RATIO = self.GAP_SIZE_RATIO
        drw.BORDER_SIZE_RATIO = self.BORDER_SIZE_RATIO
        return drw
    
    def Up_left_way(self):
        ulw = up_left_way.Up_left_way()
        ulw.GAP_SIZE_RATIO = self.GAP_SIZE_RATIO
        ulw.BORDER_SIZE_RATIO = self.BORDER_SIZE_RATIO
        return ulw
    
    def Up_right_way(self):
        urw = up_right_way.Up_right_way()
        urw.GAP_SIZE_RATIO = self.GAP_SIZE_RATIO
        urw.BORDER_SIZE_RATIO = self.BORDER_SIZE_RATIO
        return urw
    