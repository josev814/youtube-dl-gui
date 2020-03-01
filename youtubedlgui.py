import os
from sys import exit
import subprocess
import re
import requests
import time
#from Tkinter import *
from tkinter import messagebox
from tkinter import Frame,Label,BOTTOM,StringVar,Entry,Button,Tk,LEFT,OptionMenu
import datetime


APP = ''
FRAME = ''
APPW = 720
APPH = 405
SCREENW = SCREENH = APPX = APPY = None
DEBUG = True
today = datetime.datetime.now().date()
homedir = os.path.expanduser("~")
dldir = os.path.join(homedir, "Downloads")
savedir = os.path.join(homedir, "Downloads\{}-{}-{}".format(today.year, today.month, today.day))
ytdl = os.path.join(dldir,"youtube-dl.exe")
ytdl2 = os.path.join(dldir,"youtube-dl")
youtube_dl_url = 'https://youtube-dl.org/downloads/latest/youtube-dl.exe'
vidRegex = re.compile(r'^(?P<number>[0-9]+)[\s\t]+(?P<format>3gp|3gp|webm|mp4)[\s\t]+(?P<resolution>[0-9x]+)[\s\t]+(?P<info>.*)',re.IGNORECASE)
ignoreVidRegex = re.compile(r'video only', re.IGNORECASE)
VIDLIST={}
YTLINK=''


def display_message(title='Youtuble-dl', message='', mtype='info'):
    if mtype == 'error':
        messagebox.showerror(message=message)
    elif mtype == 'warning':
        messagebox.showwarning(message=message)
    else:
        messagebox.showinfo(message=message)


if os.path.exists(dldir) is False:
    display_message(
        "Missing Downloads Directory",
        "We couldn't find your Downloads directory ({}). Verify that it exists before opening this program again.".format(dldir),
        'error'
    )
    exit()

if os.path.exists(savedir) is False:
    os.mkdir(savedir)

if os.path.exists(savedir):
    os.chdir(savedir)
else:
    display_message(
        "Missing Downloads Directory",
        "We couldn't create the directory to download into ({}). Verify that it exists before opening this program again.".format(savedir),
        'error'
    )
    exit()


if os.path.exists(ytdl):
    ytdl = ytdl
elif os.path.exists(ytdl2):
    ytdl = ytdl2
else:
    display_message(
        "Missing youtube-dl.exe",
        "We couldn't find youtube-dl.exe in your Downloads directory. " +
        "We will attempt to download it now. This will take a minute.",
        'info'
    )
    r = requests.get(youtube_dl_url, allow_redirects=True, stream=True)
    with open('youtube-dl.exe', 'wb') as ytfile:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                ytfile.write(chunk)
    if os.path.exists(ytdl):
        ytdl = ytdl
    else:
        display_message(
            "Missing youtube-dl.exe",
            "We couldn't find youtube-dl.exe in your Downloads directory. " +
            "Download it using this link {}" +
            "Make sure it's in your Downloads directory. " +
            "Then restart this program.".format(youtube_dl_url),
            'error'
        )
        exit()

#upgrade youtube-dl
display_message('Youtube-dl Updating', 'Checking for youtube-dl updates, press OK to proceed')

proc = subprocess.Popen(
    [
        ytdl,
        "-U"
    ],
    stdout=subprocess.PIPE
)
while True:
    line = proc.stdout.readline().decode()
    if line != '' and DEBUG:
        print(line)
    else:
        break

def getVideoList():
    global VIDLIST
    proc = subprocess.Popen(
        [
            ytdl,
            "-F",
            YTLINK
        ],
        stdout=subprocess.PIPE
    )
    while True:
        line = proc.stdout.readline().decode()
        if line != '':
            #print "current line:", line.rstrip()
            videoMatch = re.match(
                vidRegex,
                line.rstrip()
            )
            if videoMatch:
                ignore = re.search(ignoreVidRegex, line.rstrip())
                if ignore is None:
                    videoName = '{} {} {}'.format(
                        videoMatch.group('format'),
                        videoMatch.group('resolution'),
                        videoMatch.group('info')
                    )
                    VIDLIST[videoName] = '{}'.format(videoMatch.group('number'))
        else:
            break

    if not VIDLIST: #empty dictionary
        display_message(
            "Unable to Download",
            "We are unable to download that specific YouTube video.",
            'error'
        )

def set_app_position():
    global APP, SCREENH, SCREENW, APPX, APPY
    # set screen width and height
    SCREENW = APP.winfo_screenwidth()  # width of the screen
    SCREENH = APP.winfo_screenheight()  # height of the screen
    # calculate x and y coordinates for the Tk root window
    APPX = (SCREENW / 2) - (APPW / 2)
    APPY = (SCREENH / 2) - (APPH / 2)
    if DEBUG:
        print('SCREEN %dx%d' % (SCREENW, SCREENH))
        print('APP XY %dx %dy' % (APPX, APPY))
        print('APP WxH %dx%d' % (APPW, APPH))
    APP.geometry('%dx%d+%d+%d' % (APPW, APPH, APPX, APPY))

def openFileLocation():
    opendir = messagebox.askyesno('Downloaded File', 'Would you like to open the download directory?')
    print(opendir)
    if opendir:
        print('opening {}'.format(savedir))
        subprocess.call([
            'explorer.exe',
            savedir
        ])
    exit()

def downloadFile(VIDLIST, option):
    FRAME = Frame(APP, width=APPW, height=APPH)
    nav = Frame(FRAME)
    nav.pack(side=BOTTOM, expand=True)

    label = Label(FRAME, text='Downloading File')
    label.pack()

    FRAME.pack()
    FRAME.tkraise()

    for video, key in VIDLIST.items():
        if video == option:
            proc = subprocess.Popen([ytdl, "-f", key, YTLINK], stdout=subprocess.PIPE)
            while True:
                line = proc.stdout.readline().decode()
                if line != '' and DEBUG:
                    print(line)
                else:
                    break
    openFileLocation()

def open_app():
    global APP
    APP = Tk()
    set_app_position()
    enter_video()
    APP.mainloop()

def enter_video():
    global YTLINK
    FRAME = Frame(APP, width=APPW, height=APPH)
    FRAME.winfo_toplevel().title('YouTube Video Download')
    nav = Frame(FRAME)
    nav.pack(side=BOTTOM, expand=True)

    label = Label(FRAME, text='Enter Youtube Video Link: (Paste is CTRL+V)')
    label.pack()

    youtubeLink = StringVar(FRAME)
    yt_entry = Entry(FRAME, textvariable=youtubeLink)
    yt_entry.pack()
    yt_entry.focus()

    padx = pady = 5
    submit = Button(FRAME, text='Get List', command=lambda: list_options(youtubeLink))
    submit.pack(in_=nav, side=LEFT, padx=padx, pady=pady)
    FRAME.pack()
    FRAME.tkraise()

def list_options(youtubeLink):
    global YTLINK
    YTLINK = youtubeLink.get()
    getVideoList()
    FRAME = Frame(APP, width=APPW, height=APPH)
    nav = Frame(FRAME)
    nav.pack(side=BOTTOM, expand=True)

    label = Label(FRAME, text='Select the video to download:')
    label.pack()

    videoVar = StringVar(FRAME)
    OptionMenu(FRAME, videoVar, *VIDLIST.keys()).pack()

    label = Label(FRAME, text='Application will exit when the download is complete')
    label.pack()

    padx = pady = 5
    submit = Button(FRAME, text='Download', command=lambda: downloadFile(VIDLIST, videoVar.get()))
    submit.pack(in_=nav, side=LEFT, padx=padx, pady=pady)
    FRAME.pack()
    FRAME.tkraise()

open_app()