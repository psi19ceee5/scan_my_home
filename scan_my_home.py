#!//usr/bin/env python3

import os
import sys
import subprocess
import itertools

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
        retstr = retstr + ' (' + str(self.size) + 'B)'
        return retstr

    def setWidthName(self, uwidth) :
        self.width_name = uwidth

    def setWidthFtype(self, uwidth) :
        self.width_ftyle = uwidth

    def setWidthSizestr(self, uwidth) :
        self.width_sizestr = uwidth


def str2size(sizestr) :
    if sizestr.isnumeric() :
        return float(sizestr)
    elif 'K' in sizestr :
        sizenum = sizestr.split('K')[0]
        return float(sizenum) * 1000
    elif 'M' in sizestr :
        sizenum = sizestr.split('M')[0]
        return float(sizenum) * 1000 * 1000
    elif 'G' in sizestr :
        sizenum = sizestr.split('G')[0]
        return float(sizenum) * 1000 * 1000 * 1000
    elif 'T' in sizestr :
        sizenum = sizestr.split('T')[0]
        return float(sizenum) * 1000 * 1000 * 1000 * 1000

def getUname() :
    command = "whoami"                                                                   
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, text=True)
    out, err = process.communicate()
    return out.split('\n')[0]
       
def main() :

    defaulthome = "/home/" + getUname() + "/"
    thehome = defaulthome
    
    if len(sys.argv) == 2 :
        thehome = sys.argv[1]
        if thehome[-1] != "/" :
            thehome = thehome + "/"

    if len(sys.argv) > 2 :
        print("scan_my_home.py:\n")
        print("   scans your home directory and lists all files and directories sorted by the size of their content.\n")
        print("   usage: scan_my_home.py [Directory]\n")
        return 1

    print("scanning home...", end='')
    
    command = "ls -a " + thehome
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, text=False, encoding='cp1250')
    out, err = process.communicate()

    files = str(out).split('\n')
    
    files.remove('.')
    files.remove('..')
    files.remove('')

    filelist  = []
    maxwidth_name = 0
    maxwidth_ftype = 0
    maxwidth_sizestr = 0
    for item in files :
        sys.stdout.write('.')
        sys.stdout.flush()
        
        fullpath = thehome + item

        ftype = 'f' 
        if os.path.isdir(fullpath) :
            ftype = 'd'

        IsReadable = True

        command = 'du%-sh%' + fullpath  
        process = subprocess.Popen(command.split('%'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if process.stderr.read() != '' :
            print("\nCould not access " + fullpath + ". Does the file name contain non-UTF-8 compliant characters?")
            IsReadable = False
        out, err = process.communicate()
        sizestr = out.split('\n')[0].split('\t')[0]

        if IsReadable :
            filelist.append(file_info(item, ftype, sizestr, str2size(sizestr)))

        if len(item) > maxwidth_name :
            maxwidth_name = len(item)

        if len(ftype) > maxwidth_ftype :
            maxwidth_ftype = len(ftype)

        if len(sizestr) > maxwidth_sizestr :
            maxwidth_sizestr = len(sizestr)

    for item in filelist :
        item.setWidthName(maxwidth_name)
        item.setWidthFtype(maxwidth_ftype)
        item.setWidthSizestr(maxwidth_sizestr)

    filelist.sort(key=lambda x: x.size, reverse=True)

    TotalBytes = 0
    for item in filelist :
        TotalBytes = TotalBytes + item.size

    print("\nTotal: " + str(TotalBytes) + "B")
    
    for item in filelist :
        print(item)


if __name__ == "__main__" :
    main()

