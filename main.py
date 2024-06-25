from monitoring import video_capture
from overlay import create_overlay
from threading import Thread
if __name__ == '__main__':
    capture = Thread(target=video_capture.start)
    capture.start()
    overlay = Thread(target=create_overlay, args = (video_capture,))
    overlay.start()
        
 
