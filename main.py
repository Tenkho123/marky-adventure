from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label

from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp

from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window

if platform not in ["android","ios"]:
    Window.size = (350, 650)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from map_planner import MapPlanner
import way

class MovementTracker(Widget):     
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        
    def on_touch_up(self, touch):
        dx = touch.x - touch.opos[0]
        dy = touch.y - touch.opos[1]
        if abs(dx) > abs(dy):
            # Moving left or right
            if dx > 0:
                if (self.app.way_type == "down_right" and self.app.root.ids.background.up == True) or (self.app.way_type == "up_right" and self.app.root.ids.background.down == True):
                    self.app.move_right()
                    self.app.auto_correct_pos(pressed=True)
                    self.app.root.ids.score.text = str(int(self.app.root.ids.score.text)+1)
                
            else:
                if (self.app.way_type == "down_left" and self.app.root.ids.background.up == True) or (self.app.way_type == "up_left" and self.app.root.ids.background.down == True):
                    self.app.move_left()
                    self.app.auto_correct_pos(pressed=True)
                    self.app.root.ids.score.text = str(int(self.app.root.ids.score.text)+1)
        else:
            # Moving up or down
            if dy > 0:
                if (self.app.way_type == "up_left" and self.app.root.ids.background.right == True) or (self.app.way_type == "up_right" and self.app.root.ids.background.left == True):
                    self.app.move_up()
                    self.app.auto_correct_pos(pressed=True)
                    self.app.root.ids.score.text = str(int(self.app.root.ids.score.text)+1)
            else:
                if (self.app.way_type == "down_left" and self.app.root.ids.background.right == True) or (self.app.way_type == "down_right" and self.app.root.ids.background.left == True):
                    self.app.move_down()
                    self.app.auto_correct_pos(pressed=True)
                    self.app.root.ids.score.text = str(int(self.app.root.ids.score.text)+1)

class Background(Widget):
    testmap_texture = ObjectProperty(None)
    up = False
    down = False
    left = False
    right = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.testmap_texture = Image(source = "assets/white.png").texture
        self.testmap_texture.wrap = "repeat"
        
    def scroll_textures(self,time_passed):
        if self.up == True:
            self.testmap_texture.uvpos =  self.testmap_texture.uvpos[0],(self.testmap_texture.uvpos[1] - time_passed/5) % Window.height
            
        if self.down == True:
            self.testmap_texture.uvpos =  self.testmap_texture.uvpos[0],(self.testmap_texture.uvpos[1] + time_passed/5) % Window.height
            
        if self.left == True:
            self.testmap_texture.uvpos =  (self.testmap_texture.uvpos[0] - time_passed/10) % Window.width,self.testmap_texture.uvpos[1]
            
        if self.right == True:
            self.testmap_texture.uvpos =  (self.testmap_texture.uvpos[0] + time_passed/10) % Window.width,self.testmap_texture.uvpos[1]
            
        texture = self.property("testmap_texture")
        texture.dispatch(self)
        
class Cat(Image):
    pass

class MainApp(App):
    up = False
    down = True
    left = False
    right = False
    ways = []
    way = None
    way_type = None
    current = None
    SPEED=190
    DEV_MODE = False

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)
        with open("map.txt","w"):
            pass
        mp = MapPlanner()
        mp.map_planner_activate()
        #Window.bind(on_motion=self.on_motion)
        
    def start_game(self):
        with open("map.txt") as MAP_PLANNER:
            self.READER = [[int(i) for i in j.split()] for j in MAP_PLANNER.read().split("\n")]
        self.generate_ways(10)
        self.generate_label()
    
    def reset(self):
        mp = MapPlanner()
        mp.map_planner_activate()
        
        self.frames.cancel()
        
        for way in self.ways:
            self.root.remove_widget(way[1])

        cat = self.root.ids.cat
        cat.pos = (self.root.width/2)-cat.width/2, (self.root.height/2)-cat.height/2
        self.ways.clear()
        self.SPEED = 190
        
        self.root.ids.background.up,self.root.ids.background.down,self.root.ids.background.left,self.root.ids.background.right = False,False,False,False
        self.root.remove_widget(self.root.ids["score"])
        self.root.remove_widget(self.root.ids["fail_time"])
        
        self.root.ids.start_button.opacity = 1
        self.root.ids.start_button.disabled = False
        
    def next_frame(self,time_passed):
        self.move_ways(time_passed)
        self.root.ids.background.scroll_textures(time_passed)
        self.check_generate_ways()
        self.check_collision()
        
    def check_generate_ways(self):
        for i in range(len(self.ways)):
            if i == 5 and self.ways[i][1].collide_widget(self.root.ids.cat):
                self.root.remove_widget(self.ways[0][1])
                del self.ways[0]
                try:
                    self.generate_ways(2,False)
                except Exception:
                    pass

    def generate_ways(self,times,is_start=True):
        READER = self.READER
        if is_start:
            self.root.ids.background.down = True
            self.way = way.Way()
            hidden_start = [3,0]
            READER.insert(0,hidden_start)
            # start = [3,1]
            # READER.insert(1,start)
            goal = [READER[-1][0],READER[-1][1]+1]
            READER.append(goal)
            hidden_goal = [READER[-1][0],READER[-1][1]+2]
            READER.append(hidden_goal)
            
            self.vertical_way = self.way.Vertical_way()
            self.vertical_way.size_hint = None,None
            self.vertical_way.size = (self.root.width/(self.vertical_way.GAP_SIZE_RATIO), self.root.width/(self.vertical_way.GAP_SIZE_RATIO-1.8))
            self.vertical_way.pos = (self.root.width/2-self.vertical_way.width/2, self.root.height/2-self.vertical_way.height/2)
            
            self.ways.append(["vertical",self.vertical_way])
            self.root.add_widget(self.vertical_way)
            
        for i in range(1,times):
            # VERTICAL CHECKING DOWN
            if READER[i][0]==READER[i-1][0] and READER[i][1]==READER[i-1][1]+1 and READER[i][0]==READER[i+1][0] and READER[i][1]==READER[i+1][1]-1:
                self.up = False
                self.down = True
                self.left = False
                self.right = False
                
                self.vertical_way = self.way.Vertical_way()
                self.vertical_way.size_hint = None,None
                self.vertical_way.size = (self.root.width/(self.vertical_way.GAP_SIZE_RATIO), self.root.width/(self.vertical_way.GAP_SIZE_RATIO-1.8))

                x,y = self.check_attach_coordinate("vertical",self.ways[-1][0])
                self.vertical_way.pos = (x, y)
                
                self.ways.append(["vertical",self.vertical_way])
                self.root.add_widget(self.vertical_way)
                
                continue
            
            # VERTICAL CHECKING UP
            elif READER[i][0]==READER[i-1][0] and READER[i][1]==READER[i-1][1]-1 and READER[i][0]==READER[i+1][0] and READER[i][1]==READER[i+1][1]+1:
                self.up = True
                self.down = False
                self.left = False
                self.right = False
                
                self.vertical_way = self.way.Vertical_way()
                self.vertical_way.size_hint = None,None
                self.vertical_way.size = (self.root.width/(self.vertical_way.GAP_SIZE_RATIO), self.root.width/(self.vertical_way.GAP_SIZE_RATIO-1.8))
                
                x,y = self.check_attach_coordinate("vertical",self.ways[-1][0])
                self.vertical_way.pos = (x, y)
                
                self.ways.append(["vertical",self.vertical_way])
                self.root.add_widget(self.vertical_way)
                
                continue
            
            # HORIZONTAL CHECKING RIGHT
            if READER[i][0]==READER[i-1][0]+1 and READER[i][1]==READER[i-1][1] and READER[i][0]==READER[i+1][0]-1 and READER[i][1]==READER[i+1][1]:
                self.up = False
                self.down = False
                self.left = False
                self.right = True
                
                self.horizontal_way = self.way.Horizontal_way()
                self.horizontal_way.size_hint = None,None
                self.horizontal_way.size = (self.root.width/(self.horizontal_way.GAP_SIZE_RATIO-1.8), self.root.width/(self.horizontal_way.GAP_SIZE_RATIO))
                
                x,y = self.check_attach_coordinate("horizontal",self.ways[-1][0])
                self.horizontal_way.pos = (x, y)
                
                self.ways.append(["horizontal",self.horizontal_way])
                self.root.add_widget(self.horizontal_way)
                
                continue
            
            # HORIZONTAL CHECKING LEFT
            elif READER[i][0]==READER[i-1][0]-1 and READER[i][1]==READER[i-1][1] and READER[i][0]==READER[i+1][0]+1 and READER[i][1]==READER[i+1][1]:
                self.up = False
                self.down = False
                self.left = True
                self.right = False
                
                self.horizontal_way = self.way.Horizontal_way()
                self.horizontal_way.size_hint = None,None
                self.horizontal_way.size = (self.root.width/(self.horizontal_way.GAP_SIZE_RATIO-1.8), self.root.width/(self.horizontal_way.GAP_SIZE_RATIO))
                
                x,y = self.check_attach_coordinate("horizontal",self.ways[-1][0])
                self.horizontal_way.pos = (x, y)
                
                self.ways.append(["horizontal",self.horizontal_way])
                self.root.add_widget(self.horizontal_way)
                
                continue
            
            # DOWN LEFT CHECKING LEFT NEXT
            if READER[i][0]==READER[i-1][0] and READER[i][1]==READER[i-1][1]-1 and READER[i][0]==READER[i+1][0]+1 and READER[i][1]==READER[i+1][1]:
                self.up = False
                self.down = False
                self.left = True
                self.right = False
                
                self.down_left_way = self.way.Down_left_way()
                self.down_left_way.size_hint = None,None
                self.down_left_way.size = (self.root.width/(self.down_left_way.GAP_SIZE_RATIO-.9), self.root.width/(self.down_left_way.GAP_SIZE_RATIO-.9))

                x,y = self.check_attach_coordinate("down_left",self.ways[-1][0])
                self.down_left_way.pos = (x, y)
                
                self.ways.append(["down_left",self.down_left_way])
                self.root.add_widget(self.down_left_way)
                
                continue
            
            # DOWN LEFT CHECKING DOWN NEXT
            elif READER[i][0]==READER[i-1][0]+1 and READER[i][1]==READER[i-1][1] and READER[i][0]==READER[i+1][0] and READER[i][1]==READER[i+1][1]-1:
                self.up = False
                self.down = True
                self.left = False
                self.right = False
                
                self.down_left_way = self.way.Down_left_way()
                self.down_left_way.size_hint = None,None
                self.down_left_way.size = (self.root.width/(self.down_left_way.GAP_SIZE_RATIO-.9), self.root.width/(self.down_left_way.GAP_SIZE_RATIO-.9))
                
                x,y = self.check_attach_coordinate("down_left",self.ways[-1][0])
                self.down_left_way.pos = (x, y)
                
                self.ways.append(["down_left",self.down_left_way])
                self.root.add_widget(self.down_left_way)
                
                continue
            
            # DOWN RIGHT CHECKING RIGHT
            if READER[i][0]==READER[i-1][0] and READER[i][1]==READER[i-1][1]-1 and READER[i][0]==READER[i+1][0]-1 and READER[i][1]==READER[i+1][1]:
                self.up = False
                self.down = False
                self.left = False
                self.right = True
                
                self.down_right_way = self.way.Down_right_way()
                self.down_right_way.size_hint = None,None
                self.down_right_way.size = (self.root.width/(self.down_right_way.GAP_SIZE_RATIO-.9), self.root.width/(self.down_right_way.GAP_SIZE_RATIO-.9))
                
                x,y = self.check_attach_coordinate("down_right",self.ways[-1][0])
                self.down_right_way.pos = (x, y)
                
                self.ways.append(["down_right",self.down_right_way])
                self.root.add_widget(self.down_right_way)
                
                continue
            
            # DOWN RIGHT CHECKING DOWN
            elif READER[i][0]==READER[i-1][0]-1 and READER[i][1]==READER[i-1][1] and READER[i][0]==READER[i+1][0] and READER[i][1]==READER[i+1][1]-1:      
                self.up = False
                self.down = True
                self.left = False
                self.right = False
                
                self.down_right_way = self.way.Down_right_way()
                self.down_right_way.size_hint = None,None
                self.down_right_way.size = (self.root.width/(self.down_right_way.GAP_SIZE_RATIO-.9), self.root.width/(self.down_right_way.GAP_SIZE_RATIO-.9))
                
                x,y = self.check_attach_coordinate("down_right",self.ways[-1][0])
                self.down_right_way.pos = (x, y)
                
                self.ways.append(["down_right",self.down_right_way])
                self.root.add_widget(self.down_right_way)
                
                continue
            
            # UP LEFT CHECKING LEFT
            if READER[i][0]==READER[i-1][0] and READER[i][1]==READER[i-1][1]+1 and READER[i][0]==READER[i+1][0]+1 and READER[i][1]==READER[i+1][1]:
                self.up = False
                self.down = False
                self.left = True
                self.right = False
                
                self.up_left_way = self.way.Up_left_way()
                self.up_left_way.size_hint = None,None
                self.up_left_way.size = (self.root.width/(self.up_left_way.GAP_SIZE_RATIO-.9), self.root.width/(self.up_left_way.GAP_SIZE_RATIO-.9))
                
                x,y = self.check_attach_coordinate("up_left",self.ways[-1][0])
                self.up_left_way.pos = (x, y)
                
                self.ways.append(["up_left",self.up_left_way])
                self.root.add_widget(self.up_left_way)
                
                continue
            
            # UP LEFT CHECKING UP
            elif READER[i][0]==READER[i-1][0]+1 and READER[i][1]==READER[i-1][1] and READER[i][0]==READER[i+1][0] and READER[i][1]==READER[i+1][1]+1:
                self.up = True
                self.down = False
                self.left = False
                self.right = False
                
                self.up_left_way = self.way.Up_left_way()
                self.up_left_way.size_hint = None,None
                self.up_left_way.size = (self.root.width/(self.up_left_way.GAP_SIZE_RATIO-.9), self.root.width/(self.up_left_way.GAP_SIZE_RATIO-.9))
                
                x,y = self.check_attach_coordinate("up_left",self.ways[-1][0])
                self.up_left_way.pos = (x, y)
                
                self.ways.append(["up_left",self.up_left_way])
                self.root.add_widget(self.up_left_way)
                
                continue
            
            # UP RIGHT CHECKING RIGHT
            if READER[i][0]==READER[i-1][0] and READER[i][1]==READER[i-1][1]+1 and READER[i][0]==READER[i+1][0]-1 and READER[i][1]==READER[i+1][1]:
                self.up = False
                self.down = False
                self.left = False
                self.right = True
                
                self.up_right_way = self.way.Up_right_way()
                self.up_right_way.size_hint = None,None
                self.up_right_way.size = (self.root.width/(self.up_right_way.GAP_SIZE_RATIO-.9), self.root.width/(self.up_right_way.GAP_SIZE_RATIO-.9))

                x,y = self.check_attach_coordinate("up_right",self.ways[-1][0])
                self.up_right_way.pos = (x, y)
                
                self.ways.append(["up_right",self.up_right_way])
                self.root.add_widget(self.up_right_way)
                
                continue
            
            # UP RIGHT CHECKING UP
            elif READER[i][0]==READER[i-1][0]-1 and READER[i][1]==READER[i-1][1] and READER[i][0]==READER[i+1][0] and READER[i][1]==READER[i+1][1]+1:
                self.up = True
                self.down = False
                self.left = False
                self.right = False
                
                self.up_right_way = self.way.Up_right_way()
                self.up_right_way.size_hint = None,None
                self.up_right_way.size = (self.root.width/(self.up_right_way.GAP_SIZE_RATIO-.9), self.root.width/(self.up_right_way.GAP_SIZE_RATIO-.9))
                
                x,y = self.check_attach_coordinate("up_right",self.ways[-1][0])
                self.up_right_way.pos = (x, y)
                
                self.ways.append(["up_right",self.up_right_way])
                self.root.add_widget(self.up_right_way)
                
                continue
        """
          Because the READER require 1 stading previously so it's can check [i-1] with [i] from start.
        So we must keep 1 value back to do that, else list out of range.
        """
        del self.READER[:times-1]
        if is_start:
            self.frames = Clock.schedule_interval(self.next_frame, 1/60.)
        
    def generate_label(self):
        self.root.ids["score"] = Label(text="0",font_size="40dp",
                                  size_hint_y=None,
                                  height="70dp", pos_hint={"center_x": .5})
        self.root.ids["score"].y = "40dp"
        
        self.root.ids["fail_time"] = Label(text="0",font_size="30dp",
                                      size_hint_y=None,
                                      height="28dp", pos_hint={"center_x": .5},
                                      color=(1,0,0,.9))
        self.root.ids["fail_time"].y = "20dp"
        
        self.root.add_widget(self.root.ids["score"])
        self.root.add_widget(self.root.ids["fail_time"])
        
    def check_collision(self):
        for way in self.ways:
            way_type,way = way[0],way[1]
            if way == self.ways[-1][1] and way.collide_widget(self.root.ids.cat):
                self.reset()
                
            elif way.collide_widget(self.root.ids.cat):
                self.way_type = way_type
                self.current_way = way
                self.auto_correct_pos()
    
    def check_attach_coordinate(self,current_way_type,previous_way_type,previous_way_num=-1):
        previous_way = self.ways[previous_way_num][1]
        # VERTICAL 4/4 corner and 2/2 linear
        if current_way_type == "vertical" and previous_way_type == "vertical" and self.down == True:
            return previous_way.pos[0],previous_way.pos[1]-previous_way.height
        
        if current_way_type == "vertical" and previous_way_type == "vertical" and self.up == True:
            return previous_way.pos[0],previous_way.pos[1]+previous_way.height
        
        if current_way_type == "vertical" and previous_way_type == "up_right":
            return previous_way.pos[0],previous_way.pos[1]+previous_way.height
        
        if current_way_type == "vertical" and previous_way_type == "up_left":
            ulw = self.up_left_way
            small_linear = ulw.width - ulw.root_width/ulw.GAP_SIZE_RATIO
            return previous_way.pos[0]+small_linear,previous_way.pos[1]+previous_way.height
        
        if current_way_type == "vertical" and previous_way_type == "down_right":
            vw = self.vertical_way
            return previous_way.pos[0],previous_way.pos[1]-vw.height
        
        if current_way_type == "vertical" and previous_way_type == "down_left":
            vw = self.vertical_way
            dlw = self.down_left_way
            small_linear = dlw.width - dlw.root_width/dlw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]+small_linear,previous_way.pos[1]-vw.height
        
        # HORIZONTAL 4/4 corner and 2/2 linear
        if current_way_type == "horizontal" and previous_way_type == "horizontal" and self.left == True:
            return previous_way.pos[0]-previous_way.width, previous_way.pos[1]
        
        if current_way_type == "horizontal" and previous_way_type == "horizontal" and self.right == True:
            return previous_way.pos[0]+previous_way.width, previous_way.pos[1]
        
        
        if current_way_type == "horizontal" and previous_way_type == "up_right":
            return previous_way.pos[0]+previous_way.width,previous_way.pos[1]
        
        if current_way_type == "horizontal" and previous_way_type == "up_left":
            hw = self.horizontal_way
            ulw = self.up_left_way
            
            return previous_way.pos[0]-hw.width,previous_way.pos[1]
        
        if current_way_type == "horizontal" and previous_way_type == "down_right":
            drw = self.down_right_way
            small_linear = drw.width - drw.root_width/drw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]+previous_way.width,previous_way.pos[1]+small_linear
        
        if current_way_type == "horizontal" and previous_way_type == "down_left":
            hw = self.horizontal_way
            dlw = self.down_left_way
            small_linear = dlw.width - dlw.root_width/dlw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]-hw.width,previous_way.pos[1]+small_linear
        
        # DOWN LEFT 4/4 corner and 2/2 linear
        if current_way_type == "down_left" and previous_way_type == "vertical":
            dlw = self.down_left_way
            small_linear = dlw.width - dlw.root_width/dlw.GAP_SIZE_RATIO
            return previous_way.pos[0]-small_linear,previous_way.pos[1]+previous_way.height
        
        if current_way_type == "down_left" and previous_way_type == "horizontal":
            dlw = self.down_left_way
            small_linear = dlw.width - dlw.root_width/dlw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]+previous_way.width, previous_way.pos[1]-small_linear
        
        if current_way_type == "down_left" and previous_way_type == "up_right" and self.left == True:
            urw = self.up_right_way
            small_linear = urw.width - urw.root_width/urw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]-small_linear,previous_way.pos[1]+previous_way.height
            
        if current_way_type == "down_left" and previous_way_type == "up_right" and self.down == True:
            urw = self.up_right_way
            small_linear = urw.width - urw.root_width/urw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]+previous_way.width,previous_way.pos[1]-small_linear
            
        if current_way_type == "down_left" and previous_way_type == "down_right":
            return previous_way.pos[0]+previous_way.width,previous_way.pos[1]
            
        if current_way_type == "down_left" and previous_way_type == "up_left":
            return previous_way.pos[0],previous_way.pos[1]+previous_way.height
        
        # DOWN RIGHT 4/4 corner and 2/2 linear
        if current_way_type == "down_right" and previous_way_type == "vertical":
            drw = self.down_right_way
            
            return previous_way.pos[0],previous_way.pos[1]+previous_way.height
        
        if current_way_type == "down_right" and previous_way_type == "horizontal":
            drw = self.down_right_way
            small_linear = drw.width - drw.root_width/drw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]-drw.width, previous_way.pos[1]-small_linear
        
        if current_way_type == "down_right" and previous_way_type == "up_left" and self.right == True:
            ulw = self.up_left_way
            small_linear = ulw.width - ulw.root_width/ulw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]+small_linear, previous_way.pos[1]+previous_way.height
            
        if current_way_type == "down_right" and previous_way_type == "up_left" and self.down == True:
            ulw = self.up_left_way
            small_linear = ulw.width - ulw.root_width/ulw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]-previous_way.width, previous_way.pos[1]-small_linear
        
        if current_way_type == "down_right" and previous_way_type == "down_left":
            return previous_way.pos[0]-previous_way.width, previous_way.pos[1]
            
        if current_way_type == "down_right" and previous_way_type == "up_right":
            return previous_way.pos[0], previous_way.pos[1]+previous_way.height
         
        # UP LEFT 4/4 corner and 2/2 linear
        if current_way_type == "up_left" and previous_way_type == "vertical":
            ulw = self.up_left_way
            small_linear = ulw.width - ulw.root_width/ulw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]-small_linear,previous_way.pos[1]-ulw.height
        
        if current_way_type == "up_left" and previous_way_type == "horizontal":
            return previous_way.pos[0]+previous_way.width, previous_way.pos[1]
        
        if current_way_type == "up_left" and previous_way_type == "down_right" and self.left == True:
            drw = self.down_right_way
            small_linear = drw.width - drw.root_width/drw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]-small_linear, previous_way.pos[1]-previous_way.height
        
        if current_way_type == "up_left" and previous_way_type == "down_right" and self.up == True:
            drw = self.down_right_way
            small_linear = drw.width - drw.root_width/drw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]+previous_way.width, previous_way.pos[1]+small_linear
        
        if current_way_type == "up_left" and previous_way_type == "down_left":
            return previous_way.pos[0], previous_way.pos[1]-previous_way.height
        
        if current_way_type == "up_left" and previous_way_type == "up_right":
            return previous_way.pos[0]+previous_way.width, previous_way.pos[1]
        
        # UP RIGHT 4/4 corner and 2/2 linear
        if current_way_type == "up_right" and previous_way_type == "vertical":
            urw = self.up_right_way
            
            return previous_way.pos[0],previous_way.pos[1]-urw.height
        
        if current_way_type == "up_right" and previous_way_type == "horizontal":
            urw = self.up_right_way
            
            return previous_way.pos[0]-urw.width, previous_way.pos[1]
        
        if current_way_type == "up_right" and previous_way_type == "down_left" and self.right == True:
            dlw = self.down_left_way
            small_linear = dlw.width - dlw.root_width/dlw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]+small_linear, previous_way.pos[1]-previous_way.height

        if current_way_type == "up_right" and previous_way_type == "down_left" and self.up == True:
            dlw = self.down_left_way
            small_linear = dlw.width - dlw.root_width/dlw.GAP_SIZE_RATIO
            
            return previous_way.pos[0]-previous_way.width, previous_way.pos[1]+small_linear
            
        if current_way_type == "up_right" and previous_way_type == "down_right":
            return previous_way.pos[0], previous_way.pos[1]-previous_way.height
            
        if current_way_type == "up_right" and previous_way_type == "up_left":
            return previous_way.pos[0]-previous_way.width, previous_way.pos[1]
        
    def move_ways(self,time_passed):
        for way in self.ways:
            way = way[1]
            if self.root.ids.background.up == True:
                way.y -= time_passed * self.SPEED
                
            if self.root.ids.background.down == True:
                way.y += time_passed * self.SPEED
                
            if self.root.ids.background.left == True:
                way.x += time_passed * self.SPEED
                
            if self.root.ids.background.right == True:
                way.x -= time_passed * self.SPEED
            
            #way.size = (self.root.width/way.GAP_SIZE_RATIO, self.root.width/way.GAP_SIZE_RATIO)
    
    def speed_up(self):
        self.SPEED+=10
        print(self.SPEED)
        
    def slow_down(self):
        self.SPEED-=10
        print(self.SPEED)
    
    def auto_correct_pos_activate(self,way,way_type,direction):
        '''
        This is to support the auto_correct_pos function
        '''
        
        cat = self.root.ids.cat
        
        if way_type == "down_left":
            if direction == "left":
                cat.y = self.root.height/2-cat.height/2
                a = way.pos[1]+way.height-way.default_width/(way.BORDER_SIZE_RATIO-2.5)-(cat.y+cat.height)
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[1] = way.pos[1]-a
                    
            elif direction == "down":
                cat.x = self.root.width/2-cat.width/2
                a = way.pos[0]+way.width-way.default_width/(way.BORDER_SIZE_RATIO-2.5)-(cat.x+cat.width)
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[0] = way.pos[0]-a
            return
                    
        if way_type == "down_right":
            if direction == "right":
                cat.y = self.root.height/2-cat.height/2
                a = way.pos[1]+way.height-way.default_width/(way.BORDER_SIZE_RATIO-2.5)-(cat.y+cat.height)
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[1] = way.pos[1]-a
                    
            elif direction == "down":
                cat.x = self.root.width/2-cat.width/2
                a = cat.x-(way.pos[0]+way.default_width/(way.BORDER_SIZE_RATIO-2.5))
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[0] = way.pos[0]+a
            return
        
        if way_type == "up_left":
            if direction == "left":
                cat.y = self.root.height/2-cat.height/2
                a = cat.y-(way.pos[1]+way.default_width/(way.BORDER_SIZE_RATIO-2.5))
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[1] = way.pos[1]+a
                    
            elif direction == "up":
                cat.x = self.root.width/2-cat.width/2
                a = way.pos[0]+way.width-way.default_width/(way.BORDER_SIZE_RATIO-2.5)-(cat.x+cat.width)
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[0] = way.pos[0]-a
            return
            
        if way_type == "up_right":
            if direction == "right":
                cat.y = self.root.height/2-cat.height/2
                a = cat.y-(way.pos[1]+way.default_width/(way.BORDER_SIZE_RATIO-2.5))
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[1] = way.pos[1]+a
                    
            elif direction == "up":
                cat.x = self.root.width/2-cat.width/2
                a = cat.x-(way.pos[0]+way.default_width/(way.BORDER_SIZE_RATIO-2.5))
                for way in self.ways:
                    way_type,way = way[0],way[1]
                    way.pos[0] = way.pos[0]+a
            return
            
    def auto_correct_pos(self,pressed=False):
        cat = self.root.ids.cat
        way = self.current_way
        way_type = self.way_type
        fail_time = self.root.ids.fail_time
        
        if not self.DEV_MODE:
            if way_type == "down_left":
                self.current = "down_left"
                if (cat.y + cat.height > way.pos[1] + way.height - way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.up == True) or (pressed == True and self.root.ids.background.left == True):
                    self.move_left()
                    self.auto_correct_pos_activate(way,way_type, "left")
                    
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
                    
                elif (cat.x + cat.width > way.pos[0] + way.width - way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.right == True) or (pressed == True and self.root.ids.background.down == True):
                    self.move_down()
                    self.auto_correct_pos_activate(way,way_type, "down")
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
            
            if way_type == "down_right":
                self.current = "down_right"
                if (cat.y + cat.height > way.pos[1] + way.height - way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.up == True) or (pressed == True and self.root.ids.background.right == True):
                    self.move_right()
                    self.auto_correct_pos_activate(way,way_type, "right")
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
                
                elif (cat.x < way.pos[0] + way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.left == True) or (pressed == True and self.root.ids.background.down == True):
                    self.move_down()
                    self.auto_correct_pos_activate(way,way_type, "down")
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
                
            if way_type == "up_left":
                self.current = "up_left"
                if (cat.y < way.pos[1] + way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.down == True) or (pressed == True and self.root.ids.background.left == True):
                    self.move_left()
                    self.auto_correct_pos_activate(way,way_type, "left")
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
                
                elif (cat.x + cat.width +1> way.pos[0]+way.width-way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.right == True) or (pressed == True and self.root.ids.background.up == True):
                    self.move_up()
                    self.auto_correct_pos_activate(way,way_type, "up")
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
                
            if way_type == "up_right":
                self.current = "up_right"
                if (cat.y < way.pos[1] + way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.down == True) or (pressed == True and self.root.ids.background.right == True):
                    self.move_right()
                    self.auto_correct_pos_activate(way,way_type, "right")
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
                
                elif (cat.x < way.pos[0]+way.default_width/way.BORDER_SIZE_RATIO and self.root.ids.background.left == True) or (pressed == True and self.root.ids.background.up == True):
                    self.move_up()
                    self.auto_correct_pos_activate(way,way_type, "up")
                    if pressed == False:
                        fail_time.text = str(int(fail_time.text)+1)
        
        
    def move_up(self):
        self.root.ids.background.up = True
        self.root.ids.background.down = False
        self.root.ids.background.left = False
        self.root.ids.background.right = False
    
    def move_down(self):
        self.root.ids.background.up = False
        self.root.ids.background.down = True
        self.root.ids.background.left = False
        self.root.ids.background.right = False
    
    def move_left(self):
        self.root.ids.background.up = False
        self.root.ids.background.down = False
        self.root.ids.background.left = True
        self.root.ids.background.right = False
    
    def move_right(self):
        self.root.ids.background.up = False
        self.root.ids.background.down = False
        self.root.ids.background.left = False
        self.root.ids.background.right = True
    
    def pause_screen(self):
        if self.root.ids.pause_button.text == "Resume":
            self.root.ids.pause_button.background_normal = "assets/pause_icon.png"
            self.root.ids.pause_button.text = ""
            self.frames = Clock.schedule_interval(self.next_frame, 1/60.)
            
        else:
            self.root.ids.pause_button.background_normal = "assets/transparent.png"
            self.root.ids.pause_button.text = "Resume"
            self.frames.cancel()
    
    """
    def on_motion(self, etype, me, alpha):
        if me == "begin":
            self.speed_changing = Clock.schedule_interval(self.speed_up,1/10)
            try:
                self.trigger.cancel()
            except Exception:
                pass
            
        if me == "end":
            self.speed_changing.cancel()
            self.trigger = Clock.schedule_once(self.trigger_slow_down, 2)  
    
    def trigger_slow_down(self, timed_pass):
        self.speed_changing = Clock.schedule_interval(self.slow_down,1/2)
    """
    
    def trigger_dev_mode(self):
        self.DEV_MODE = True
    
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        print("keyboard:",keyboard)
        
        # W
        if keyboard == 119:
            if self.DEV_MODE == True:
                self.move_up()
                
            elif (self.way_type == "up_left" and self.root.ids.background.right == True) or (self.way_type == "up_right" and self.root.ids.background.left == True):
                self.move_up()
                self.auto_correct_pos(pressed=True)
                self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
            
        # A
        if keyboard == 97:
            if self.DEV_MODE == True:
                self.move_left()
                
            elif (self.way_type == "down_left" and self.root.ids.background.up == True) or (self.way_type == "up_left" and self.root.ids.background.down == True):
                self.move_left()
                self.auto_correct_pos(pressed=True)
                self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
                
        # S
        if keyboard == 115:
            if self.DEV_MODE == True:
                self.move_down()
            
            elif (self.way_type == "down_left" and self.root.ids.background.right == True) or (self.way_type == "down_right" and self.root.ids.background.left == True):
                self.move_down()
                self.auto_correct_pos(pressed=True)
                self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
                
        # D
        if keyboard == 100:
            if self.DEV_MODE == True:
                self.move_right()
                
            elif (self.way_type == "down_right" and self.root.ids.background.up == True) or (self.way_type == "up_right" and self.root.ids.background.down == True):
                self.move_right()
                self.auto_correct_pos(pressed=True)
                self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
        
    
if __name__ == "__main__":
    MainApp().run()