#GoPro_timestamp.py
#Created by Chris Rillahan
#Last Updated: 1/30/2015
#Written with Python 2.7.2, OpenCV 2.4.8

#This script uses ffprobe to interogate a MP4 file and extract the creation time.
#This information is then used to initiate a counter/clock which is used to put
#the timestamp on each frame of the video.  The videos are samed as *.avi files
#using DIVX compression due to the availability in OpenCV.  The audio is stripped
#out in this script.

import cv2, os, sys, subprocess, shlex, re, time
import datetime as dt
from subprocess import call
from dateutil import parser
from glob import glob

#Name of the file
# filename = '/Users/hongseokoh/Documents/GitHub/GoPro-Timestamp/F20A2610-A669-4122-A3A8-6F8F1F770152.MP4'

#This function initiates a call to ffprobe which returns a summary report about
#the file of interest.  The returned information is then parsed to extract only
#the creation time of the file.

def creation_time(filename):
    import os, sys, subprocess, shlex, re
    from subprocess import call

    cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"filename: {filename}")
    out, err =  p.communicate()
    # subprocess.call(['exiftool', '''"-filecreatedate<createdate"''', filename ])

    if err:
        print("========= error ========")
        print(err)

    t = out.splitlines()
    print(t)
    apple_time = False
    for i, t_temp in enumerate(t):
        if 'TAG:com.apple.quicktime.creationdate' in t_temp.decode():
            apple_time = True
            apple_idx = i

    if apple_time:
        time = t[apple_idx] #TAG:com.apple.quicktime.creationdate
        time = time.decode().split('=')[-1]
        time = time.split('+')[0]
    else:
        time = t[14][18:37] # creation_time
        

    print(f"creation time: {time}")

    return time
def timestamp_video(filename):
    #Opens the video import and sets parameters
    video = cv2.VideoCapture(filename)

    #Checks to see if a the video was properly imported
    status = video.isOpened()

    if status == True: 
        FPS = video.get(cv2.CAP_PROP_FPS)
        width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        size = (int(width), int(height))
        total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_lapse = (1/FPS)*1000

        #Initializes time origin of the video
        t = creation_time(filename)
        # initial = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        initial = parser.parse(t)
        timestamp = initial 

        #Initializes the export video file
        # codec = cv2.VideoWriter.fourcc('D','I','V','X') # avi
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        temp_name = filename[:-4] + 'temp.MP4'
        out_name = filename.replace('input_video', 'timestamped_video')
        video_out = cv2.VideoWriter(temp_name, codec, FPS, size, 1)

        #Initializes the frame counter
        current_frame = 0
        start = time.time()
    #    print("Press 'esc' to quit.")

        #Reads through each frame, calculates the timestamp, places it on the frame and
        #exports the frame to the output video.
        while current_frame < total_frames:
            subprocess.call(['clear'])
            print(f"filename: {filename}")
            print(f"creation time: {initial}")
            print(f"FPS: {FPS}")
            print(f"size: {width}x{height}")
            print(f"{int(current_frame)}/{int(total_frames)}")

            success, image = video.read()
            print(f"status: {success}")
            if not success:
                break
            
            elapsed_time = video.get(cv2.CAP_PROP_POS_MSEC)
            current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
            timestamp = initial + dt.timedelta(microseconds = elapsed_time*1000)
    #        print(timestamp)
            cv2.putText(image, 'Date: ' + str(timestamp)[0:10], (50,int(height-150)), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 3)
            cv2.putText(image, 'Time: ' + str(timestamp)[11:-4], (50,int(height-100)), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 3)
            video_out.write(image)
    #        cv2.imshow('Video', image)

            k = cv2.waitKey(10)
            if k == 27:
                break
        
        video.release()
        video_out.release()
        cv2.destroyAllWindows()

        #Calculate how long the timestampping took
        duration = (time.time()-float(start))/60
        if initial.hour >= 19 or (total_frames/FPS) < 5:
            subprocess.call(['mv', temp_name, out_name])
        else:
            subprocess.call(['ffmpeg', '-i', temp_name, '-s', '1920x1080', '-vcodec', 'libx264', '-acodec', 'aac', out_name])
            subprocess.call(['rm', temp_name])
            
        subprocess.call(['rm', filename])

        print("Video has been timestamped")
        print('This video took:' + str(duration) + ' minutes')

    else:
        print('Error: Could not load video')


if __name__ == "__main__":
    base_dir = '/Users/hongseokoh/Documents/GitHub/GoPro-Timestamp/input_video/'
    ext_list = ['MP4']
    filenames = []

    for ext in ext_list:
        filenames += list(glob(base_dir + f"*.{ext}"))
    
    for filename in filenames:
        timestamp_video(filename)