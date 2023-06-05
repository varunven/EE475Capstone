import socketio
import json
import threading
import time
import alsaaudio


# The ObjectRecognitionWorker class starts the object recognition service on a seperate thread, where it
# uses a socket to connect to the YOLO server. Via the socket, it receives detected objects, and relays them
# as audio. Takes in a priority table, which is used to fetch priorities of different objects, and reset
# the priorities via web requests. Takes in the confidence threshold for object recognition such that
# all detections with a condience less than the minimum threshold are discarded. Also takes in the audio
# controller to play/save audio files. Takes in the yolo server link to connect to the server and receive
# detections
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

    # Updates the detections buffer, filtering out detections that are redundant from the previous scene.
    # After filtering out redundant detections, only updates buffer with ten objects with the highest recognition
    # priority as set by the user, then plays out the newly detected objects in the new scene.
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

    # handles web app requests related to object recognition. Involves requests such as enabling/disabling object
    # recognition audio, updating the recognition priority of different objects, changing the volume of audio relays,
    # and changing the audio playback time.
    def handle_event(self, event):
        self.volumeControl = event.volumeControl
        self.isAudioOn = event.isAudioOn
        self.voiceGender = event.voiceGender # does not look doable in gtts- can instead change accent by using uk-en
        self.priority_table.update_priorities(event.objsPriority)
        self.audioPlaybackTime = event.audioPlaybackTime
        
        m = alsaaudio.Mixer()
        if(self.isAudioOn):
            m.setvolume(int(self.volumeControl))
        else:
            m.setvolume(0)

        response = "Updated state values for object recognition"
        print(response)
        return response

    # Connects the socket to the YOLO server. Attempts to reconnect every 5 seconds on disconnect.
    # Defines different event handlers depending on the event received by the socket from the YOLO server.
    def connect_to_server(self):

        # service identifies itself as obj recognition service to YOLO server on connect
        @self.socket.event
        def connect():
            print('Object Recognition Service: connected to YOLO server')
            self.socket.emit('see_rasp_pi')
        
        # tells the user that the service has disconnected on disconnect         
        @self.socket.event
        def disconnect():
            print('Object Recognition Service: disconnected from YOLO server')
            
        # handles the "detections" event emitted by the YOLO server. Receives detections from the server,
        # parses them, and calls self.update_detections_buffer to update the new detections and relay the
        # detections as audio
        @self.socket.event
        def detections(detections):
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
        try:
            self.socket.connect(self.link)
            self.socket.wait()
        except Exception as e:
            print("Object Recognition Service: YOLO server not yet started. Attempting to reconnect...")
            time.sleep(5)
            self.connect_to_server()