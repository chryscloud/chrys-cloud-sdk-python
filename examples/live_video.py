import chrysalis
import time
import cv2
import os
from time import strftime

ch = chrysalis.RtmpMedia(host="127.0.0.1", port="1111", password="aaaaaaaaa", ssl_ca_cert="test.cer")

os.environ['DISPLAY'] = ":0"

if __name__ == "__main__":
    
    while True:
        img = ch.VideoLatestImage()

        if img is not None:
            frame = img.data
            # draw current time on the screen
            cv2.putText(frame, strftime("%H:%M:%S"), (10,100), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,255,0),2,cv2.LINE_AA)
            cv2.imshow("720p/20 FPS live video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
