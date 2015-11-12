__author__ = 'kenhansen'
"""
THIS SCRIPT GOES THROUGH A FOLDER OF MOV FILES AND RUNS FFMPEG's BLACKDETECT FUNCTION GENERATING A LOG FILE.
THE LOG FILE IS THEN READ AND THE BLACK_START TIMES ARE CONVERTED TO TIME CODE AND ANOTHER TXT DOCUMENT IS OUTPUT.

ASSUMPTIONS:
This script assumes all MOV files are 23.98fps. I haven't put in provisions for other frame rates.

STEP 1: TKinter asks for the directory of MOV files and stores that as 'directory'.
STEP 2: Python goes through the directory and does the following on all files ending in '.mov'
STEP 3: FFMPEG Black Detect is run on each MOV file generating a LOG as .txt.
STEP 4: The LOG is read into Python and parsed for information.
STEP 5: Python tries to locate the start time code of the MOV file based on the LOG. If none is detected the user is
prompted for the start timecode of the MOV in hhmmssff format.
    I would like to make it so one is also asked if this start TC will be the same for all MOV's in the folder so it
    doesn't ask for every MOV.
STEP 6: Python locates the frame rate of the MOV file based on the LOG. (again, this script assumes all MOVs are 23.98)
STEP 7: Python then locates all lines containing "black_start" and parses out the start time and saves it to an array.
STEP 8: Python then does the calculations needed to convert the black start times from seconds to time code.
STEP 9: Python then adds the hours, minutes, seconds, frames of the black start times to the MOV start time code.
STEP 10: Python creates a TXT document with the file name, MOV start TC, MOV frame rate, and a list of all start time
codes for all blacks.
"""

import subprocess
import sys, os
import Tkinter as tk
import tkFileDialog

root = tk.Tk()
root.withdraw()

def StartTC(log_file):
    hh=()
    mm=()
    ss=()
    ff=()
    rate=()
    for line in log_file:
        if line.startswith('      timecode'):
            colon=line.find(':')
            hh=line[colon+2:colon+4]
            mm=line[colon+5:colon+7]
            ss=line[colon+8:colon+10]
            ff=line[colon+11:colon+13]
        if line.startswith('    Stream #0:0'):
            fps=line.find('fps')
            rate=line[fps-6:fps-1]
    return hh, mm, ss, ff, rate

def getblackstarts(log_file):
    black_starts=[]
    for line in log_file:
        if 'blackdetect' in line:
            b_s=line.find('black_start')
            b_e=line.find('black_end')
            blacktimestart=line[b_s+12:b_e-1]
            black_starts.append(blacktimestart)
    return black_starts

def TCCalculations(black_start, hh, mm, ss, ff):
    bdr = float(black_start)*.999
    bdrhh = int(bdr / 3600)
    bdrmm = int(bdr / 60)
    bdrss = int(bdr - (bdrmm * 60))
    bdrff = int(((bdr - int(bdr)) * 24) + 1)
    newhh = hh + bdrhh
    newmm = mm + bdrmm
    newss = ss + bdrss
    newff = ff + bdrff
    return newhh, newmm, newss, newff

def timecode(h, m, s, f):
    if h < 10:
        h = '0'+str(h)
    if m < 10:
        m = '0'+str(m)
    if s < 10:
        s = '0'+str(s)
    if f < 10:
        f = '0'+str(f)
    return h, m, s, f

print "Choose the source directory for the MOV files"
directory = tkFileDialog.askdirectory()
AllMOVTCs = 'n'

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(".mov"):
            full_file = str(os.path.join(root, file))
            full_file = full_file.replace(" ","\ ")
            path = os.path.dirname(full_file)
            logfile=os.path.join(path, str(full_file[:-4]+"_FFMPEGLOG.txt"))
            subprocess.call('ffmpeg -i '+full_file+' -vf blackdetect=d=2:pic_th=0.97:pix_th=0.1 -an -f null - 2>'+logfile, shell=True)
            logfile=logfile.replace("\ "," ")
            with open(logfile, 'r') as log_file:
                (hh, mm, ss, ff, rate) = StartTC(log_file)
                if hh==() and mm==() and ss==() and ff==():
                    if AllMOVTCs == 'n':
                        print "No Timecode in metadata.\n"
                        userTC = raw_input("Enter the start timecode of the movie file excluding colons (hhmmssff)\n")
                        print "You entered "+userTC+"\n"
                        AllMOVTCs = raw_input("Will this be the start TC for all MOV files? [y/n]")
                        MOVTC = userTC[0:2]+":"+userTC[2:4]+":"+userTC[4:6]+":"+userTC[6:]
                        print 'User Entered Start TimeCode is '+MOVTC
                        hh=int(userTC[0:2])
                        mm=int(userTC[2:4])
                        ss=int(userTC[4:6])
                        ff=int(userTC[6:])
                    else:
                        hh=int(userTC[0:2])
                        mm=int(userTC[2:4])
                        ss=int(userTC[4:6])
                        ff=int(userTC[6:])
                else:
                    MOVTC = str(hh)+':'+str(mm)+':'+str(ss)+':'+str(ff)
                    print 'Start TimeCode is '+ MOVTC
                print 'The frame rate is '+str(rate)
                log_file.seek(0)
                (black_starts) = getblackstarts(log_file)
                blacktc=[]
                for i in range(len(black_starts)):
                    hh=int(hh)
                    mm=int(mm)
                    ss=int(ss)
                    ff=int(ff)
                    (newhh, newmm, newss, newff) = TCCalculations(black_starts[i], hh, mm, ss, ff)
                    if newff >= 24:
                        newss = newss+1
                        newff = newff-24
                    if newss >= 60:
                        newmm = newmm+1
                        newss = newss-60
                    if newmm >=60:
                        newhh = newhh+1
                        newmm = newmm-60
                    (blackhh, blackmm, blackss, blackff) = timecode(newhh, newmm, newss, newff)
                    blacktc.append(str(blackhh)+':'+str(blackmm)+':'+str(blackss)+':'+str(blackff))
            f=open(logfile[:-15]+"_BLACKS.txt", 'w')
            f.write("LIST OF BLACKS AND THEIR START TIME CODES\n\n")
            f.write("MOV File: "+file+"\n")
            f.write("Start Timecode of MOV File: "+MOVTC+"\n")
            f.write("Frame Rate of the MOV File: "+str(rate)+"fps\n\n")
            f.write("BLACKS:\n")
            for i in range(len(blacktc)):
                f.write("Black starts at TC "+blacktc[i]+"\n")
            f.close()
