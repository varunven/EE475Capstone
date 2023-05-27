from constants.priorities import coco_objects_priority

class PriorityTable():
    
    def __init__(self):
        self.priorities = coco_objects_priority

    def update_priority(self, object_name, new_priority):
        if 1 <= new_priority <= 100:
            if object_name in self.priorities:
                self.priorities[object_name] = new_priority
            else:
                print(f"{object_name} not found in priorities list")
        else:
            print("Priority value must be in-between 1-100 inclusive")

    def get_priority(self, object_name):
        return self.priorities[object_name]
    
    # want it inplace or no?
    def sort_by_priority(self, detections_array):
        return sorted(detections_array, key= lambda detection: self.priorities[detection['class']])