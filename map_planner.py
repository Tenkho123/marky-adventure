from pyamaze import maze

"""
only run pyamaze once then loop
"""
class MapPlanner():
    is_start = True #Check if run first time to not generate random bridge
    save_goal = 3 #Basically save previous end for new start
    current_height = None
    rows = 10
    columns = 10
    way_limit = 200
    # Coords for the total way generator
    map_coord_list = []
    last_height = 0
    
    def map_planner(self):
        """
        Thanks pyazmaze module for the get correct path function
        """
        m = maze(self.rows,self.columns)
        m.CreateMaze(x=1,y=self.save_goal,rev=self.rows)
        
    def map_planner_activate(self):
        """
        1|       4|   
        2| ====> 5|  The height of 2 layouts is 6 so the next 3 continue the pre 3
        3|       6|  
        """
        self.current_height = self.last_height
        while True:
            if len(self.map_coord_list) < self.way_limit:
                if self.is_start:
                    self.map_planner()  
                    self.is_start = False
                    
                if not self.is_start:
                    with open("map_temp.txt","r") as map_temp:
                        get_current_map = [[int(i) for i in j.split()] for j in map_temp.read().split("\n")]
                    get_current_map_m = [[i[0],i[1]+self.current_height] for i in get_current_map]
                    
                    self.current_height = self.current_height + get_current_map[-1][1]
                    
                    for i in get_current_map_m:
                        self.map_coord_list.append(i)
                    
                    # Save coord for next layer
                    self.save_goal = get_current_map[-1][0]
                    
            else:
                del self.map_coord_list[self.way_limit:]
                # Writing coord to map.txt from map_coord_list
                with open("map.txt","w") as map_coord:       
                    for i in self.map_coord_list:
                        for j in i:
                            map_coord.write("%s " %j)
                        if i != self.map_coord_list[-1]:
                            map_coord.write("\n")
                break
        self.last_height = self.map_coord_list[-1][1]
        self.map_coord_list.clear()
        
if __name__ == "__main__":
    m = MapPlanner()
    m.map_planner_activate()