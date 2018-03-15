########################################
# Simple script that performs an incremental, one-directional backup between two folders (src and dst).
# File comparison is done by checking last update date and size of the file.
#
# Arguments: src, dst, errorLog
#   src Path of source folder
#   dst Path of destination folder
#   errorLog Path of error log file
#
# Path of backup log file is always dst/backup_log.txt. This file is ignored when calculating deletions.
# Backup file MUST always be present on dst but NEVER on src. This is checked as a safety measure.
# Hidden items directly under src or dst are ignored. This is done to allow system folders on media devices.
########################################

import os
import shutil
import sys
import time

######## HIDDEN ITEM DETECTION #########
# Code from https://stackoverflow.com/a/14063074

if os.name == 'nt':
    # pip install pywin32
    import win32api
    import win32con


def itemIsHidden(p):
    if os.name == 'nt':
        attribute = win32api.GetFileAttributes(p)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    else:
        return p.startswith('.')  # linux-osx


################ GLOBAL ################

backupLogName = "backup_log.txt"

toAdd = []
toDelete = []

added = 0
deleted = 0
processed = 0

processing = None
status = "FAILED"

startTime = time.time()


################# FUNC #################

def getElapsedTime():
    global startTime
    return time.strftime("%H:%M:%S", time.gmtime(time.time() - startTime))


def printWithElapsedTime(line):
    print("[" + getElapsedTime() + "] " + line)


def logError(line):
    with open(errorLogFile, "a") as error_log:
        error_log.write(line + '\n')


# Compute difference of contents from src to dst. Performs recursive calls for matching items on src and dst.
def computeDiff(src, dst, depth):
    global backupLogName
    global processed

    processed += 1

    # Ignore hidden files on root folder (that allows backing up device root folders)
    if depth != 1 or (not itemIsHidden(src) and not itemIsHidden(dst)):

        # Both are files
        if os.path.isfile(src) and os.path.isfile(dst):

            srcStats = os.stat(src)
            dstStats = os.stat(dst)

            # File was modified or size is different
            if srcStats.st_mtime != dstStats.st_mtime or srcStats.st_size != dstStats.st_size:
                toDelete.append(dst)
                toAdd.append((src, dst))

        # One of them is a file and the other a folder
        elif os.path.isfile(src) or os.path.isfile(dst):
            toDelete.append(dst)
            toAdd.append((src, dst))

        # Both are folders
        else:
            src_items = os.listdir(src)
            dst_items = os.listdir(dst)

            for item in src_items:
                if item in dst_items:
                    # Item is on both src and dst
                    computeDiff(os.path.join(src, item), os.path.join(dst, item), depth + 1)
                else:
                    # Item is only on src
                    toAdd.append((os.path.join(src, item), os.path.join(dst, item)))

            for item in dst_items:
                if item != backupLogName and item not in src_items:
                    # Item is only on dst and not backup_log
                    toDelete.append(os.path.join(dst, item))


# Deletes item from dst
def delete(dst):
    global processing
    global deleted

    printWithElapsedTime("Del > " + dst)
    processing = dst

    if os.path.isfile(dst):
        os.remove(dst)
    else:
        shutil.rmtree(dst)

    processing = None
    deleted += 1


# Copies item from src to dst
def add(src, dst):
    global processing
    global added

    printWithElapsedTime("Add > " + dst)
    processing = dst

    if os.path.isfile(src):
        shutil.copy2(src, dst)
    else:
        shutil.copytree(src, dst)

    processing = None
    added += 1


################# MAIN #################

timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(startTime))
printWithElapsedTime("Starting backup on " + timestamp)

if len(sys.argv) < 4:
    logError("[" + timestamp + "] 3 arguments needed: src, dst, errorLog")
    printWithElapsedTime("3 arguments needed: source, destination, errorLog")
    exit(1)

rootSrc = sys.argv[1]
rootDst = sys.argv[2]
errorLogFile = sys.argv[3]
backupLogFile = os.path.join(rootDst, backupLogName)

if backupLogName in os.listdir(rootSrc):
    logError("[" + timestamp + "] Backup log found on source folder: " + rootSrc)
    printWithElapsedTime("Backup log found on source folder: " + rootSrc)
    exit(2)

if backupLogName not in os.listdir(rootDst):
    logError("[" + timestamp + "] Backup log not found on destination folder: " + rootDst)
    printWithElapsedTime("Backup log not found on destination folder: " + rootDst)
    exit(3)

try:
    printWithElapsedTime("Computing differences...")
    computeDiff(rootSrc, rootDst, 0)
    printWithElapsedTime(str(len(toAdd)) + " additions, " + str(len(toDelete)) + " deletions")

    for deletion in toDelete:
        delete(deletion)

    for addition in toAdd:
        add(addition[0], addition[1])

    status = "OK"
    printWithElapsedTime("Finished backup")
    exit(0)

except Exception as e:
    logError("[" + timestamp + "] Unknown exception: " + str(e))
    printWithElapsedTime("Unknown exception: " + str(e))
    exit(3)

finally:
    with open(backupLogFile, "a") as backup_log:
        backup_log.write(
            '{"timestamp": "' + timestamp + '", "status": "' + status + '", "elapsed": "' + getElapsedTime() +
            '", "processed": "' + str(processed) + '", "added": "' + str(added) + '", "deleted": "' + str(deleted) +
            '", "failed": "' + str(processing) + '"}\n')
