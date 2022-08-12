#!//usr/bin/env python3

import os
import sys
import subprocess
import itertools
import argparse

class file_info :
    
    def __init__(self, uname, uftype, usizestr, usize) :
        self.name = uname
        self.ftype = uftype
        self.sizestr = usizestr
        self.size = usize
        self.width_name = 45
        self.width_ftype = 3
        self.width_sizestr = 7

    def __str__(self) :
        retstr = 'Name: ' + '{name:<{num}}'.format(name=self.name, num=self.width_name)
        retstr = retstr + '\tType: ' + '{ftype:<{num}}'.format(ftype=self.ftype, num=self.width_ftype)
        retstr = retstr + '\tSize: ' + '{sizestr:<{num}}'.format(sizestr=self.sizestr, num=self.width_sizestr)
        retstr = retstr + ' (' + str(self.size) + 'K)'
        return retstr

    def setWidthName(self, uwidth) :
        self.width_name = uwidth

    def setWidthFtype(self, uwidth) :
        self.width_ftyle = uwidth

    def setWidthSizestr(self, uwidth) :
        self.width_sizestr = uwidth

        
suffixes = ['K', 'M', 'G', 'T']


def print_error(message) :
    sys.stdout.write('\033[0;31m\n[ERROR]: {text} \033[0m\n'.format(text=message))
    sys.stdout.flush()


def print_warning(message) :
    
    sys.stdout.write('\033[0;33m\n[WARNING]: {text} \033[0m\n'.format(text=message))
    sys.stdout.flush()


def str2size(sizestr) :
    
    if sizestr.isnumeric() :
        return float(sizestr) * 1000 # assume default unit K

    factor = 1
    for suff in suffixes :
        if suff in sizestr :
            sizenum = sizestr.split(suff)[0]
            return float(sizenum) * factor
        else :
            factor = factor * 1000
    

def size2str(size) :
    
    nit = 0
    while size / 1000 > 1 :
        size = size / 1000.
        nit = nit + 1

    if size / 10 < 1 :
        size = round(size * 10) / 10
    else :
        size = round(size)

    return str(size) + suffixes[nit]


def getUname() :
    
    command = "whoami"                                                                   
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, text=True)
    out, err = process.communicate()
    return out.split('\n')[0]


def scan_file(upath, ufilelist, uftype) :

    command = 'du%-s%' + upath
    process = subprocess.Popen(command.split('%'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.stderr.read() != '' :
        print_warning("Could not access " + upath + ". Do you have read permissions to all files? Does the file name contain non-UTF-8 compliant characters?")
        return '', 'ERROR'
    out, err = process.communicate()

    size = float(out.split('\n')[0].split('\t')[0])

    sizestr = size2str(size)
    ufilelist.append(file_info(upath, uftype, sizestr, size))

    sys.stdout.write('.')
    sys.stdout.flush()

    return out, err


def scan_dir(udir, ufilelist, recursive=False) :

    command = "ls%-a%" + udir
    process = subprocess.Popen(command.split('%'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False, encoding='cp1250')
    if process.stderr.read() != '' :
        print_warning("Could not access " + udir + ". Do you have read permissions to all files? Does the file name contain non-UTF-8 compliant characters?")
        return '', 'ERROR'
    out, err = process.communicate()
    
    files = str(out).split('\n')
    
    files.remove('.')
    files.remove('..')
    files.remove('')
    
    for item in files :

        if udir[-1] == "/" :
            fullpath = udir + item
        else :
            fullpath = udir + "/" + item
        
        ftype = 'f' 
        if os.path.isdir(fullpath) :
            ftype = 'd'

        if ftype == 'f' or not recursive :
            out, err = scan_file(fullpath, ufilelist, ftype)
        else :
            out, err = scan_dir(fullpath, ufilelist, recursive=recursive)

    return out, err


def main() :

    defaulthome = "/home/" + getUname() + "/"
    thehome = defaulthome

    parser = argparse.ArgumentParser(description='Scan and sort files by size.')
    parser.add_argument('-d', metavar='DIR', type=str, required=False, help='override the directory DIR to be scanned.')
    parser.add_argument('-r', action='store_true', help='Recursice scanning: list all files in all subfolders.')
    args = parser.parse_args()

    if args.d :
        thehome = args.d
        if thehome[-1] != "/" :
            thehome = thehome + "/"

    print("scanning " + thehome + " ", end='')

    filelist  = []
    scan_dir(thehome, filelist, recursive=args.r)

    maxwidth_name = 0
    maxwidth_ftype = 0
    maxwidth_sizestr = 0

    for item in filelist :
        if len(item.name) > maxwidth_name :
            maxwidth_name = len(item.name)

        if len(item.ftype) > maxwidth_ftype :
            maxwidth_ftype = len(item.ftype)

        if len(item.sizestr) > maxwidth_sizestr :
            maxwidth_sizestr = len(item.sizestr)


    for item in filelist :
        item.setWidthName(maxwidth_name)
        item.setWidthFtype(maxwidth_ftype)
        item.setWidthSizestr(maxwidth_sizestr)

    filelist.sort(key=lambda x: x.size, reverse=True)

    TotalBytes = 0
    for item in filelist :
        TotalBytes = TotalBytes + item.size

    print("\nTotal: " + size2str(TotalBytes) + " (" + str(TotalBytes) + "B)")
    print("Number of files: " + len(filelist))
    
    for item in filelist :
        print(item)


if __name__ == "__main__" :
    main()

