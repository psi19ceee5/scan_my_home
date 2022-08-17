#!/usr/bin/env python3

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
        self.width_sizestr = 10

    def __str__(self) :
        retstr = 'Size: ' + '{sizestr:<{num}}'.format(sizestr=self.sizestr, num=self.width_sizestr+2)
        retstr = retstr + ' (' + '{size:<{num}}'.format(size=str(self.size)+'K)', num=self.width_size+5)
        retstr = retstr + 'Type: ' + '{ftype:<{num}}'.format(ftype=self.ftype, num=self.width_ftype+2)
        retstr = retstr + 'Name: ' + '{name:<{num}}'.format(name=self.name, num=self.width_name+2)
        return retstr

    def setWidthName(self, uwidth) :
        self.width_name = uwidth

    def setWidthFtype(self, uwidth) :
        self.width_ftyle = uwidth

    def setWidthSizestr(self, uwidth) :
        self.width_sizestr = uwidth

    def setWidthSize(self, uwidth) :
        self.width_size = uwidth


class progress_indicator :
    
    def __init__(self, frequency=1, maxc=0, symb=".", recursiveopts=False) :
        self._recursiveopts = recursiveopts
        self._frequency = frequency
        self._maxc = maxc
        self._symb = symb
        self._counter = 0
        self._symbcnt = 0
        self.setRecursiveOpts()

    def setRecursive(self, recursiveopts) :
        self._recursiveopts = recursiveopts
        self.setRecursiveOpts()

    def setRecursiveOpts(self) :
        if self._recursiveopts :
            self._frequency = 100
            self._maxc = 10

    def resetCounter(self) :
        self._counter = 0

    def resetSymbCnt(self) :
        self._symbcnt = 0

    def emit(self) :
        if self._counter % self._frequency == 0 :
            sys.stdout.write(self._symb)
            self._symbcnt = self._symbcnt + 1
            if self._symbcnt == self._maxc :
                sys.stdout.write('\b'*self._maxc)
                sys.stdout.flush()
                sys.stdout.write(' '*self._maxc)
                sys.stdout.write('\b'*self._maxc)
                sys.stdout.flush()
                self.resetSymbCnt()
            sys.stdout.flush()
        self._counter = self._counter + 1


suffixes = ['K', 'M', 'G', 'T']
progind = progress_indicator()


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


def scan_file(upath, ufilelist, uftype, verbose=False) :

    command = 'du%%%-s%%%' + upath
    process = subprocess.Popen(command.split('%%%'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.stderr.read() != '' :
        print_warning("Could not access file " + upath + ". Do you have read permissions to all files? Does the file name contain non-UTF-8 compliant characters?")
        return '', 'ERROR'
    out, err = process.communicate()

    size = float(out.split('\n')[0].split('\t')[0])

    sizestr = size2str(size)
    ufilelist.append(file_info(upath, uftype, sizestr, int(size)))
    if verbose :
        print(str(len(ufilelist)) + " -- " + upath)
    else:
        progind.emit()

    return out, err


def scan_dir(udir, ufilelist, recursive=False, verbose=False) :

    command = "ls%%%-a%%%" + udir
    process = subprocess.Popen(command.split('%%%'), stdout=subprocess.PIPE, stderr=None, text=False, encoding='cp1250')
    try :
        out, err = process.communicate()
    except UnicodeDecodeError :
        print_warning("Caught execption of type UnicodeDecodeError. Skipping directory " + udir + ".")
        return '', 'ERROR'
    
    files = str(out).split('\n')

    if '.' in files :
        files.remove('.')
    if '..' in files :
        files.remove('..')
    if '' in files :
        files.remove('')
    
    for item in files :

        if udir[-1] == "/" :
            fullpath = udir + item
        else :
            fullpath = udir + "/" + item

        if os.path.islink(fullpath) :
            continue
        
        ftype = 'f' 
        if os.path.isdir(fullpath) :
            ftype = 'd'
            
        if ftype == 'f' or not recursive :
            out, err = scan_file(fullpath, ufilelist, ftype, verbose=verbose)
        else :
            out, err = scan_dir(fullpath, ufilelist, recursive=recursive, verbose=verbose)

    return out, err


def main() :

    defaulthome = "/home/" + getUname() + "/"
    thehome = defaulthome

    parser = argparse.ArgumentParser(description='Scan and sort files by size.')
    parser.add_argument('-r', action='store_true', help='recursice scanning: list all files in all subfolders.')
    parser.add_argument('-v', action='store_true', help='increase verbosity.')
    parser.add_argument('-d', metavar='DIR', type=str, required=False, help='override the directory DIR to be scanned.')
    parser.add_argument('-f', metavar='FILE', type=str, required=False, help='specify output file for the results. If no output file is given, results are written to stdout.')
    args = parser.parse_args()

    if args.d :
        thehome = args.d
        if thehome[-1] != "/" :
            thehome = thehome + "/"

    progind.setRecursive(args.r)

    print("scanning " + thehome + " ", end='')

    filelist  = []
    scan_dir(thehome, filelist, recursive=args.r, verbose=args.v)

    maxwidth_name = 0
    maxwidth_ftype = 0
    maxwidth_sizestr = 0
    maxwidth_size = 0

    for item in filelist :
        if len(item.name) > maxwidth_name :
            maxwidth_name = len(item.name)
        if len(item.ftype) > maxwidth_ftype :
            maxwidth_ftype = len(item.ftype)
        if len(item.sizestr) > maxwidth_sizestr :
            maxwidth_sizestr = len(item.sizestr)
        if len(str(item.size)) > maxwidth_size :
            maxwidth_size = len(str(item.size))

    for item in filelist :
        item.setWidthName(maxwidth_name)
        item.setWidthFtype(maxwidth_ftype)
        item.setWidthSizestr(maxwidth_sizestr)
        item.setWidthSize(maxwidth_size)

    filelist.sort(key=lambda x: x.size, reverse=True)

    TotalBytes = 0
    for item in filelist :
        TotalBytes = TotalBytes + item.size

    printstr1 = "Total: " + size2str(TotalBytes) + " (" + str(TotalBytes) + "K)"
    printstr2 = "Number of files: " + str(len(filelist))

    orig_stdout = sys.stdout

    if args.f :
        sys.stdout = open(args.f, 'w')

    print("\n" + printstr1)
    print(printstr2)
    for item in filelist :
        print(item)

    sys.stdout = orig_stdout
    sys.stdout.write("\n")
    sys.stdout.flush()


if __name__ == "__main__" :
    main()

