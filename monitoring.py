import av
import time
import numpy as np
import threading
import keyboard
from collections import deque
import json
import re

input_device_full = json.load(open('config.json'))['selected_device']
def parse_device_name(full_name):
    pattern = r'"(.*?)" \(video\)'
    match = re.search(pattern, full_name)
    if match:
        device_name = "video="+match.group(1)
        return device_name
    return "video="+full_name
input_device = parse_device_name(input_device_full)
#input_device = 'video=Game Capture 4K60 Pro MK.2'
buffer_size = 134217728  # 128MB buffer size
monitoring_duration = 300  #5 minutes


class VideoInfo:
    def __init__(self):
        self.width = None
        self.height = None
        self.resolution = None
        self.frame_rate = None
        self.codec_name = None
        self.fps_list = []
        self.timestamps = deque()

    def update(self, container):
        stream = container.streams.video[0]
        self.width = stream.width
        self.height = stream.height
        self.resolution = f"{self.width}x{self.height}"
        self.frame_rate = eval(str(stream.average_rate))
        self.codec_name = stream.codec_context.name
        self.fps_list.append(self.frame_rate)
        self.timestamps.append(time.time())

    def calculate_metrics(self):
        #removes old values based on the monitoring duration
        current_time = time.time()
        while self.timestamps and current_time - self.timestamps[0] > monitoring_duration:
            self.fps_list.pop(0)
            self.timestamps.popleft()

        if len(self.fps_list) == 0:
            return None, None
        avg_fps = np.mean(self.fps_list)
        low_1_fps = np.percentile(self.fps_list, 1)
        return avg_fps, low_1_fps

    def reset_metrics(self):
        self.fps_list.clear()
        self.timestamps.clear()

class VideoCapture:
    def __init__(self, input_device, buffer_size, capture_interval=0.1):
        self.input_device = input_device
        self.buffer_size = buffer_size
        self.capture_interval = capture_interval
        self.video_info = VideoInfo()
        self.stop_event = threading.Event()
        self.capture_thread = threading.Thread(target=self.capture_data)
        self.frame_deque = deque(maxlen=1)
        self.non_duplicate_frame_count = 0
        self.previous_frame = None

    def get_video_info(self):
        container = av.open(self.input_device, format='dshow', options={'rtbufsize': str(self.buffer_size)})
        self.video_info.update(container)
        container.close()

    def capture_data(self):
        while not self.stop_event.is_set():
            t0 = time.time()
            self.get_video_info()
            avg_fps, low_1_fps = self.video_info.calculate_metrics()
            data = {
                'resolution': self.video_info.resolution,
                'frame_rate': f"{self.video_info.frame_rate:.2f}",
                'avg_fps': f"{avg_fps:.2f}",
                'low_1_fps': f"{low_1_fps:.2f}",
                'codec': self.video_info.codec_name
            }
            self.frame_deque.append(data)
            text = (f'Resolution: {self.video_info.resolution}\n'
                    f'Frame Rate: {self.video_info.frame_rate} FPS\n'
                    f'Avg FPS: {avg_fps:.2f}\n'
                    f'1% Low FPS: {low_1_fps:.2f}\n'
                    f'Codec: {self.video_info.codec_name}')
            print(text)
            t1 = time.time()
            time.sleep(max(0, self.capture_interval - (t1 - t0)))

    def start(self):
        self.capture_thread.start()

    def stop(self):
        self.stop_event.set()
        self.capture_thread.join()
        avg_fps, low_1_fps = self.video_info.calculate_metrics()
        print(f"Avg FPS: {avg_fps:.2f}, 1% Low FPS: {low_1_fps:.2f}")

keyboard.add_hotkey('ctrl+q', lambda: video_capture.stop())

video_capture = VideoCapture(input_device, buffer_size, capture_interval=0.1)

