import cv2
import numpy as np
import time
import math
import threading
import handtrackingmodule as htm  # Ensure your hand detection module is correct
import os

def set_volume(level):
    """Set system volume (0 to 100)."""
    os.system(f"osascript -e 'set volume output volume {level}'")

set_volume(50)  

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

# Function to Set Volume in Background Thread
def set_volume_thread(volume):
    threading.Thread(target=set_volume, args=(volume,)).start()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb
        x2, y2 = lmList[8][1], lmList[8][2]  # Index Finger
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Center

        # Draw Circles
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        # Calculate Distance
        length = math.hypot(x2 - x1, y2 - y1)
        volume = np.interp(length, [20, 250], [0, 100])

        # Run Volume Update in Background
        set_volume_thread(volume)

        # Change Color if Fingers are Close
        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    # Calculate FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("video", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)