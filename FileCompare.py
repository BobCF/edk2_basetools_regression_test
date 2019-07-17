## @file
# Compare files
#
# Copyright (c) 2019, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
#

##
# Import Modules
#

from __future__ import print_function
import sys
import os
import difflib
import filecmp


def PrintDiffFile(rt, file1, DirPath):
    Lines = []
    for i in rt:
        Lines.append(i)
    if not Lines:
        return True
    FileLines = '\n'.join(Lines)
    if not DirPath:
        DirPath = os.getcwd()
    path = file1.replace(os.sep, '-').replace('.', '-')[3:]
    FilePath = os.path.join(DirPath, ''.join([path, '.diff']))
    with open(FilePath, 'w') as File:
        File.write(FileLines)
    return FilePath


def CompareTextSortFile(file1, file2):
    with open(file1, 'r') as OrgFile:
        OrgLines = OrgFile.readlines()
    with open(file2, 'r') as NewFile:
        NewLines = NewFile.readlines()
    content_new = [item.strip() for item in OrgLines if item.strip()]
    content_org = [item.strip() for item in NewLines if item.strip()]
    content_org.sort()
    content_new.sort()
    rt = difflib.unified_diff(content_org, content_new)
    return rt


def CompareTextFile(file1, file2):
    with open(file1, 'r') as OrgFile:
        OrgLines = OrgFile.readlines()
    with open(file2, 'r') as NewFile:
        NewLines = NewFile.readlines()
    rt = difflib.unified_diff(OrgLines, NewLines)
    return rt


def CompareMakefile(file1, file2, DirPath):
    rt = CompareTextSortFile(file1, file2)
    return PrintDiffFile(rt, file1,DirPath)


def CompareC(file1, file2, DirPath):
    rt = CompareTextFile(file1, file2)
    return PrintDiffFile(rt, file1,DirPath)


def CompareH(file1, file2, DirPath):
    rt = CompareTextFile(file1, file2)
    return PrintDiffFile(rt, file1, DirPath)


def CompareTimeStamp(file1, file2, DirPath):
    rt = CompareTextSortFile(file1, file2)
    return PrintDiffFile(rt, file1, DirPath)


def CompareDepex(file1, file2, DirPath):
    return False


def CompareLst(file1, file2,DirPath):
    rt = CompareTextSortFile(file1, file2)
    return PrintDiffFile(rt, file1, DirPath)


def CompareMap(file1, file2,DirPath):
    pass


def CheckFileExt(file1, file2):
    Ext = os.path.splitext(file1)[-1]
    if Ext == '':
        if file1.endswith('Makefile') and file2.endswith('Makefile'):
            return 'Makefile'
        elif file1.endswith('AutoGenTimeStamp') and file2.endswith('AutoGenTimeStamp'):
            return 'AutoGenTimeStamp'
    elif Ext == os.path.splitext(file2)[-1]:
        return Ext
    return False


def CompareFunc(file1, file2, Func, DirPath):
    return Func(file1, file2, DirPath)


FileTypeDict = {'Makefile': CompareMakefile, '.map': CompareMap, 'AutoGenTimeStamp': CompareTimeStamp,
                '.lst': CompareLst, '.depex': CompareDepex, '.c': CompareC, '.h': CompareH}


def CompareFile(file1, file2, DirPath=None):
    if not (os.path.exists(file1) and os.path.exists(file2)):
        return False
    if filecmp.cmp(file1, file2) == True:
        return True
    Ext = CheckFileExt(file1, file2)
    if not Ext or Ext not in FileTypeDict:
        return False
    Res = CompareFunc(file1, file2, FileTypeDict[Ext], DirPath)
    return Res


if __name__ == '__main__':
    file1, file2 = sys.argv[1], sys.argv[2]
    DirPath = None
    if sys.argv[3:]:
        DirPath = sys.argv[3]
    CompareFile(file1, file2, DirPath)
