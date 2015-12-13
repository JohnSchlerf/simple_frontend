# The MythTV frontend is not performing well on my computer.
# But, VLC does fine. So, this simplifies VLC launches.

import os
import Tkinter as tk
from PIL import Image, ImageTk

RECORDING_FOLDER = '/var/lib/mythtv/recordings'

def group_files(list_of_files):
    '''
    USAGE:
        grouped_list = group_files(list_of_files)

    Associates the recording with its screenshot, returns a
    list of dictionary objects
    '''
    recordings = []
    images = []
    for file in list_of_files:
        if '.mpg' in file:
            if '.png' in file[-4:]:
                images.append(file)
            elif '.mpg' in file[-4:]:
                recordings.append(file)
    grouped_list = []
    # This is a very, very lazy & dumb way to do this.
    for [recording, image] in zip(recordings, images):
        grouped_list.append({
            'recording': recording,
            'screenshot': image
            })
    return grouped_list

def get_image(file_name):
    '''
    Wrapper to load an image
    '''
    return ImageTk.PhotoImage(
        Image.open(
            os.path.join(RECORDING_FOLDER, file_name)
            )
        )

class MyFrontEnd:

    def __init__(self):
        all_files = os.listdir(RECORDING_FOLDER)
        self.grouped_files = group_files(all_files)
        self.num_videos = len(self.grouped_files)
        self.current_video = 0
        self.root = tk.Tk()
        initial_image = get_image(self.grouped_files[0]['screenshot'])
        self.panel = tk.Label(self.root, image = initial_image)
        self.panel.image = initial_image
        self.panel.pack(side="bottom", fill="both", expand="yes")
        self.root.bind("<Return>", lambda x: self.play_video())
        self.root.bind("f", lambda x: self.go_down())
        self.root.bind("j", lambda x: self.go_up())
        self.root.bind("q", lambda x: self.root.destroy())
        self.root.mainloop()

    def photo_callback(self):
        img = get_image(self.grouped_files[self.current_video]['screenshot'])
        self.panel.configure(image = img)
        self.panel.image = img

    def go_down(self):
        '''
        '''
        self.current_video += -1
        if self.current_video < 0:
            self.current_video += self.num_videos
        self.photo_callback()

    def go_up(self):
        '''
        '''
        self.current_video += 1
        if self.current_video >= self.num_videos:
            current_video -= self.num_videos
        self.photo_callback()

    def play_video(self):
        '''
        '''
        command = "cvlc "
        current_mpg = self.grouped_files[self.current_video]['recording']
        command += os.path.join(RECORDING_FOLDER, current_mpg)
        print command

if __name__=="__main__":
    MyFrontEnd()    
