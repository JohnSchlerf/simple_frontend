# The MythTV frontend is not performing well on my computer.
# But, VLC does fine. So, this simplifies VLC launches.

import os
import Tkinter as tk
from PIL import Image, ImageTk
import datetime
import mysql.connector as msq

DATABASE_PARAMS = {
    'user': 'mythtv',
    'password': 'mythtv',
    'host': '127.0.0.1',
    'database': 'mythconverg'
    }
RECORDING_FOLDER = '/var/lib/mythtv/recordings'

def format_string(in_string, max_line_length=48, max_lines=4):
    '''
    '''
    words = in_string.split()
    out_string = ''
    cur_line = 0
    cur_line_length = 0
    for word in words:
        if cur_line_length == 0:
	    out_string += word
	elif cur_line_length + len(word) < max_line_length - 1:
	    out_string += " " + word
	    cur_line_length += 1 # for the space
	elif cur_line < max_lines:
	    out_string += "\n" + word
	    cur_line_length = 0
            cur_line += 1
        cur_line_length += len(word)
    return out_string

def load_recordings():
    '''
    USAGE:
        recording_struct = load_recordings()

    Opens a connection to mysql, loads recordings,
    formats 'em as a funky structure.
    '''
    connection = msq.connect(**DATABASE_PARAMS)
    cursor = connection.cursor()
    query = "select chanid, starttime, title, subtitle, description "
    query += "from recorded order by starttime"
    cursor.execute(query)
    all_shows = cursor.fetchall()
    recording_dict = {}
    for show in all_shows:
        video = str(show[0]) + "_" + show[1].strftime("%Y%m%d%H%M%S.mpg")
	this_dict = {
	    'subtitle': show[3],
            'date': show[1],
            'description': format_string(show[4]),
            'recording': RECORDING_FOLDER + '/' + video,
            'screenshot': RECORDING_FOLDER + '/' + video + '.png'
	    }
        if show[2] in recording_dict.keys():
	    recording_dict[show[2]].append(this_dict)
        else:
            recording_dict[show[2]] = [this_dict]
    return recording_dict

def group_files(list_of_files):
    '''
    USAGE:
        grouped_list = group_files(list_of_files)

    Associates the recording with its screenshot, returns a
    list of dictionary objects
    '''
    recordings = []
    images = []
    showing_dates = []
    for one_file in list_of_files:
        if '.mpg' in one_file:
            if '.png' in one_file[-4:]:
                images.append(one_file)
                recordings.append(one_file.replace('.png',''))
		the_date = datetime.datetime.strptime(
		    one_file[5:17], "%Y%m%d%H%M"
		    )
		the_date = (
		    the_date + datetime.timedelta(hours=-8)
		    ).strftime("%A, %B %d, %Y, at %I:%M %p")
                showing_dates.append(the_date)
    grouped_list = []
    # This is a very, very lazy & dumb way to do this.
    for [recording, image, showing_date] in \
	    zip(recordings, images, showing_dates):
        grouped_list.append({
            'recording': recording,
            'screenshot': image,
	    'date': showing_date
            })
    return grouped_list

def get_image(file_name, scale=2):
    '''
    Wrapper to load an image
    '''
    if os.path.exists(file_name):
        the_image = Image.open(
	    os.path.join(RECORDING_FOLDER, file_name)
	    )
    else:
        the_image = Image.open(
	    "/home/john/simple_frontend/blank_image.png"
            )
    w, h = the_image.size
    new_size = (int(w*scale), int(h*scale))
    return ImageTk.PhotoImage(the_image.resize(new_size))

class MyFrontEnd:
    def __init__(self):
        #all_files = os.listdir(RECORDING_FOLDER)
        #self.grouped_files = group_files(all_files)
        self.show_dict = load_recordings()
	self.show_list = self.show_dict.keys()
	self.current_show = 0
	self.grouped_files = self.show_dict[self.show_list[self.current_show]]
	self.num_videos = len(self.grouped_files)
        self.current_video = 0
        self.root = tk.Tk()
	self.image_scale = 2.5
	font = ('Helvetica', 24) 
	initial_title = self.show_list[self.current_show]
	# Title:
	self.title_panel = tk.Label(self.root, text=initial_title, font=font)
	self.title_panel.text = initial_title
	self.title_panel.pack(side="top", fill="both", expand="yes")
	# Screenshot:
        initial_image = get_image(
	    self.grouped_files[0]['screenshot'],
            self.image_scale
            )
        self.screenshot_panel = tk.Label(self.root, image = initial_image)
        self.screenshot_panel.image = initial_image
        self.screenshot_panel.pack(side="top", fill="both", expand="yes")
        # Date:
	initial_text = self.grouped_files[0]['date']
        self.date_panel = tk.Label(
	    self.root, 
	    text = initial_text,
	    font = font
	    )
	self.date_panel.text = initial_text
        self.date_panel.pack(side="top", fill="both", expand="yes")
        # Description?
	initial_description = self.grouped_files[0]['description']
	self.description_panel = tk.Label(
	    self.root,
	    text = initial_description,
	    font = font
	    )
	self.description_panel.text = initial_description
	self.description_panel.pack(side="bottom", fill="both", expand="yes")
	# Callbacks:
	self.root.bind("<Return>", lambda x: self.play_video())
        self.root.bind("g", lambda x: self.prev_title())
        self.root.bind("h", lambda x: self.next_title())
        self.root.bind("f", lambda x: self.go_down())
        self.root.bind("j", lambda x: self.go_up())
        self.root.bind("q", lambda x: self.root.destroy())
        self.root.bind("=", lambda x: self.size_up())
        self.root.bind("-", lambda x: self.size_down())
	self.root.bind("+", lambda x: self.size_up())
	self.root.bind("_", lambda x: self.size_down())
        self.root.mainloop()

    def photo_callback(self):
        img = get_image(
	    self.grouped_files[self.current_video]['screenshot'],
            self.image_scale
            )
        the_date = self.grouped_files[self.current_video]['date']
	self.title_panel.configure(text = self.show_list[self.current_show])
	self.screenshot_panel.configure(image = img)
        self.screenshot_panel.image = img
        self.date_panel.configure(text = the_date)
	#self.date_panel.text = the_date        
	description = self.grouped_files[self.current_video]['description']
	self.description_panel.configure(text = description)

    def switch_title(self, increment):
	'''
	'''
	self.current_show += increment
	if self.current_show >= len(self.show_list):
	    self.current_show = 0
	elif self.current_show < 0:
	    self.current_show += len(self.show_list)
	self.grouped_files = self.show_dict[self.show_list[self.current_show]]
	self.current_video = 0
	self.num_videos = len(self.grouped_files)
	self.photo_callback()

    def next_title(self):
	self.switch_title(1)

    def prev_title(self):
	self.switch_title(-1)

    def size_up(self):
        '''
	'''
	self.image_scale += 0.25
	self.image_scale = min(self.image_scale, 4.0)
        self.photo_callback()

    def size_down(self):
        '''
	'''
	self.image_scale += -0.25
	self.image_scale = max(self.image_scale, 1.0)
	self.photo_callback()

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
            self.current_video -= self.num_videos
        self.photo_callback()

    def play_video(self):
        '''
        '''
        command = "vlc "
        #print self.grouped_files[self.current_video]
        current_mpg = self.grouped_files[self.current_video]['recording']
        command += os.path.join(RECORDING_FOLDER, current_mpg)
        command += " --play-and-exit vlc://quit"
	self.description_panel.configure(text = "NOW PLAYING...")
	self.root.update()
        print command
        os.system(command)

if __name__=="__main__":
    MyFrontEnd()    
