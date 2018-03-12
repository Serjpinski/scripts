##############################
# Simple script that performs an incremental, one-directional backup between two folders.
# File comparison is done by checking last update date and size of the file.
##############################

import os
import shutil
import time

########### GLOBAL ###########

rootSrc = "D:"
rootDst = "E:"
errorLogFile = "C:/BACKUP ERROR.txt"
backupLogName = "backup_log.txt"
backupLogFile = os.path.join(rootDst, backupLogName)

added = 0
updated = 0
deleted = 0
ignored = 0
processing = None
status = "FAILED"

startTime = time.time()

########### FUNC ###########

def getElapsedTime():
    global startTime
    return time.strftime("%H:%M:%S", time.gmtime(time.time() - startTime))

def printWithElapsedTime(line):
    print("[" + getElapsedTime() + "] " + line)

def logError(line):
    with open(errorLogFile, "a") as error_log:
        error_log.write(line + '\n')

# Deletes item from dst, copies item from src, or both
def syncFile(src, dst, mode):

    global processing
    global added
    global updated
    global deleted

    if mode == "add":
        printWithElapsedTime("Add > " + src)
        processing = src
    elif mode == "update":
        printWithElapsedTime("Upd > " + dst)
        processing = dst
    else:
        printWithElapsedTime("Del > " + dst)
        processing = dst

    if mode != "add":
        if os.path.isfile(dst):
            os.remove(dst)
        else:
            shutil.rmtree(dst)

    if mode != "delete":
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)

    processing = None

    if mode == "add":
        added += 1
    elif mode == "update":
        updated += 1
    else:
        deleted += 1

# Syncs contents on src to dst. Performs recursive calls for matching items on src and dst.
def syncRec(src, dst):

    global backupLogName
    global ignored

    # Both are files
    if os.path.isfile(src) and os.path.isfile(dst):

        srcStats = os.stat(src)
        dstStats = os.stat(dst)

        # File was modified or size is different
        if srcStats.st_mtime != dstStats.st_mtime or srcStats.st_size != dstStats.st_size:
            syncFile(src, dst, "update")
        else:
            ignored += 1

    # One of them is a file and the other a folder
    elif os.path.isfile(src) or os.path.isfile(dst):
        syncFile(src, dst, "update")

    # Both are folders
    else:
        src_items = os.listdir(src);
        dst_items = os.listdir(dst);

        for item in src_items:
            if item in dst_items:
                # Item is on both src and dst
                syncRec(os.path.join(src, item), os.path.join(dst, item))
            else:
                # Item is only on src
                syncFile(os.path.join(src, item), os.path.join(dst, item), "add")

        for item in dst_items:
            if item != backupLogName and item not in src_items:
                # Item is only on dst and not backup_log
                syncFile(os.path.join(src, item), os.path.join(dst, item), "delete")

########### MAIN ###########

timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(startTime))
printWithElapsedTime("Starting backup on " + timestamp)

if backupLogName in os.listdir(rootSrc):
    logError("[" + timestamp + "] Backup log found on source folder: " + rootSrc)
    printWithElapsedTime("Backup log found on source folder: " + rootSrc)
    exit(1)

if backupLogName not in os.listdir(rootDst):
    logError("[" + timestamp + "] Backup log not found on destination folder: " + rootDst)
    printWithElapsedTime("Backup log not found on destination folder: " + rootDst)
    exit(2)

try:
    syncRec(rootSrc, rootDst)
    status = "OK"
    printWithElapsedTime("Finished backup")
    exit(0)

except Exception as e:
    logError("[" + timestamp + "] Unknown exception: " + str(e))
    printWithElapsedTime("Unknown exception: " + str(e))
    exit(3)

finally:
    with open(backupLogFile, "a") as backup_log:
        backup_log.write('{"timestamp": "' + timestamp + '", "status": "' + status + '", "elapsed": "' + getElapsedTime() + '", "added": "' + str(added) + '", "updated": "' + str(updated) + '", "deleted": "' + str(deleted) + '", "ignored": "' + str(ignored) + '", "failed": "' + str(processing) + '"}\n')
