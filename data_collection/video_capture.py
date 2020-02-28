"""A method to do video capture for a set number of frames from computer camera"""

import cv2
import time 
import os
import json

def video_capture():
    video_capture_0 = cv2.VideoCapture(0)

    # Number of frames to capture
    #frames = 300 # 10sec
    #frames = 1800 # 1min
    #frames = 18000 # 10min
    frames = 63000 # 35min

    # extra frames to ensure full capture
    extra_frames = 30
    frames += extra_frames

    #define frame height and width 
    frame_width0 = int(video_capture_0.get(3))
    frame_height0 = int(video_capture_0.get(4))

    # create directory for storage if it does not exist
    video_path = './DATA/videos/'
    if not os.path.exists(video_path):
        os.makedirs(video_path)

    path, dirs, files = next(os.walk(video_path))
    file_count = len(files)
    store_video_path = video_path + 'video' + str(file_count) + '.avi'

    # create output file
    out0 = cv2.VideoWriter(store_video_path, cv2.VideoWriter_fourcc(str('X'),str('V'),str('I'),str('D')), 30.0, (frame_width0,frame_height0))

    # start on frame 0
    counter = 0
    ret0, frame0 = video_capture_0.read()

    start_time = time.time()
    while True:
        counter += 1
        # Capture frame-by-frame
        ret0, frame0 = video_capture_0.read()

        if (ret0):
            # write to video
            out0.write(frame0)

        if counter == frames:
            end_time = time.time()
            break

    # When everything is done, release the capture
    video_capture_0.release()
    out0.release()
    cv2.destroyAllWindows() # closes all frames

    timestamps = {}
    timestamps['start_time'] = start_time
    timestamps['stop_time'] = end_time

    info_path = './DATA/video_info/'
    path, dirs, files = next(os.walk(info_path))
    file_count = len(files)
    store_info_path = info_path + 'info' + str(file_count) + '.json'

    with open(store_info_path, 'w') as outfile:
            json.dump(timestamps, outfile)

    time_passed = end_time - start_time

video_capture()
print('Video capture finished')