from constants.priorities import coco_objects_priority

class PriorityTable():
    
    def __init__(self):
        self.priorities = coco_objects_priority

    def update_priorities(self, new_priorities):
        self.priorities = new_priorities

    def get_priority(self, object_name):
        return self.priorities[object_name]
    
    # want it inplace or no?
    def sort_by_priority(self, detections_array):
        lambda detection: print(detection)
        return sorted(detections_array, key= lambda detection: self.priorities[detection['class']])
