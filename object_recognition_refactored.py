import socketio
import json
import threading
import time
import alsaaudio
#from utils.audio import play_audio



class ObjectRecognitionWorker:

    socket = socketio.Client()

    def __init__(self, server_link, priority_table, conf_thresh, audio_controller):
        self.audioPlaybackTime = 5
        self.detection_count = 0
        self.link = server_link
        self.detections_buffer = []
        self.priority_table = priority_table
        self.conf_thresh = conf_thresh
        self.audio_controller = audio_controller
        threading.Thread(target=self.connect_to_server).start()

    def update_detections_buffer(self, new_detections):
        # get detections that were not present in existing detections buffer
        updated_detections = [new_obj for new_obj in new_detections if new_obj not in self.detections_buffer]

        # new objects detected, remove redundant objects and add new ones
        # if scene did not change (all objects still in scene), do not play audio (dont do anything)
        # sort updated detections by priority, and include only top n detections
        # update detections_buffer
        if (updated_detections):
          self.detections_buffer = self.priority_table.sort_by_priority(updated_detections)[:10]      
          audio_string = ''
          for detection in self.detections_buffer:
              audio_string += str(detection["count"]) + ' ' + str(detection["class"])
          if (audio_string):
            #self.audio_controller.acquire_audio_lock()
            self.audio_controller.play_audio(audio_string)
            #self.audio_controller.release_audio_lock()

    def handle_event(event):
        self.volume = event.volume
        self.dist = event.dist # done in server code
        self.audioEnable = event.audioEnable
        self.objRecognitionVoice = event.objRecognitionVoice # does not look doable in gtts- can instead change accent by using uk-en
        self.objMap = event.objMap
        self.audioPlaybackTime = event.audioPlayBackTime
        
        # possible way to change volume
        m = pyalsaaudio.Mixer('PCM')
        current_volume = m.getvolume()
        if(self.audioEnable):
            m.setvolume(self.volume)
        else:
            m.setvolume(0)
            
        # update the file in constants called priority.py
        new_file_str = "coco_objects_priority = {\n"
        for key,value in self.objMap.items():
            new_file_str += (key + ": " + value + ",\n")
        new_file_str = new_file_str[:-2]
        new_file_str += "\n}"
        with open("constants/priorities.py", "w") as f:
            f.write(new_file_str)
    def connect_to_server(self):

        @self.socket.event
        def connect():
            print('Object Recognition Service: connected to YOLO server')
            self.socket.emit('see_rasp_pi')
                 
        @self.socket.event
        def disconnect():
            print('Object Recognition Service: disconnected from YOLO server')
            
        @self.socket.event
        def detections(detections):
            audio_string = 'Detected '
            self.detection_count += 1

            # output sound for each fifth detection
            if (self.detection_count % self.audioPlaybackTime == 0):
                filtered_detections = []
                for detection in json.loads(detections):
                    print(detection)
                    _confidence = detection['confidence']
                    _class = detection['class']
                    _count = detection['count']

                    # remove detections with conf < conf_thresh
                    for conf in _confidence:
                        if (float(conf) < self.conf_thresh):
                            _count -= 1
                    if _count > 0:
                      filtered_detections.append({"class": _class, "count": _count})

                self.update_detections_buffer(filtered_detections)
                    
                    #audio_string += str(_count) + ' ' + str(_class)

                #play_audio(audio_string)
            #print(self.detection_count)

        try:
            self.socket.connect(self.link)
            self.socket.wait()
        except Exception as e:
            print("Object Recognition Service: YOLO server not yet started. Attempting to reconnect...")
            time.sleep(5)
            self.connect_to_server()


