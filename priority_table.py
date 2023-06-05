from constants.priorities import coco_objects_priority

# The PriorityTable class defines the recognition priority for the different recognizable objects in the COCO dataset.
# The class allows for updating the priorities of different objects, and sorting arrays of detections as per their
# current priority. The priority of each object is an integer between 1 and 10, with 10 being the highest priority.
class PriorityTable():
    
    def __init__(self):
        self.priorities = coco_objects_priority

    # updates the priorities map; a dictionary mapping each object to its priority (1-10)
    def update_priorities(self, new_priorities):
        self.priorities = new_priorities

    # returns the priority of a specific object
    def get_priority(self, object_name):
        return self.priorities[object_name]
    
    # sorts an array of detections based on their current priority
    def sort_by_priority(self, detections_array):
        lambda detection: print(detection)
        return sorted(detections_array, key= lambda detection: self.priorities[detection['class']])
