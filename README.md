# BlackDetect

THIS SCRIPT GOES THROUGH A FOLDER OF MOV FILES AND RUNS FFMPEG's BLACKDETECT FUNCTION GENERATING A LOG FILE.
THE LOG FILE IS THEN READ AND THE BLACK_START TIMES ARE CONVERTED TO TIME CODE AND ANOTHER TXT DOCUMENT IS OUTPUT.

ASSUMPTIONS:
This script assumes all MOV files are 23.98fps. I haven't put in provisions for other frame rates.

Requires TKinter module.

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

