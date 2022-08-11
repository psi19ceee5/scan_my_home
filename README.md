######################

Author: Philip Ruehl

Date: 09.08.2022

######################

Description:

Python script that scans the user's home directory and emits a list of all files and folders
at the top level sorted by their size -- largest to smallest. With an optional argument,
other directories than /home/$USER can be scanned and sorted in the same manner. The script
is meant to give guidance to a human who wants to clean up large and messy folders on devices 
with limited disk resources.

usage: scan_my_home.py [-h] [-d DIR]

optional arguments:
  -h, --help  show this help message and exit
  -d DIR      override the directory DIR to be scanned.
  -r          Recursice scanning: list all files in all subfolders.
