#!/usr/bin/python
import psutil
import time
import sys
import subprocess
import os
import glob
import fnmatch
import socket
import shutil

def main(argv):
    repoPath = '/'.join(sys.argv[0].split('/')[:-1])
    print('repo path is : ' + repoPath)
    if len(sys.argv) == 5:
        dataFolder = sys.argv[1]
        numShanks = float(sys.argv[2])
        waittime = float(sys.argv[3]) # time interval, in seconds, in between starting new extraction/clustering jobs
        numJobs = float(sys.argv[4])  # max number of jobs to run at once
        cpuLimit = float(sys.argv[5]) # max cpu usage allowed before starting new jobs
    else:
        waittime = 600
        numJobs = 3
        cpuLimit = 90
        dataFolder = '/zpool/tingley/DT5'  # directory with recording subdirectories
        # dataFolder = '/mnt/packrat/userdirs/david/zpool1/DT6'#  # directory with recording subdirectorie
        # dataFolder = '/zpool/tingley/DT4'  # directory with recording subdirectorie
        numShanks =  10 # set this value to the number of shanks to cluster (adding ref sites as shanks)

    while True:
        os.chdir(dataFolder)
        print('searching for unprocessed recordings...')
        for dirName, subdirList, fileList in os.walk(dataFolder):
            for file in fileList:
                if file.startswith(dirName.split('/')[-1]) & file.endswith(".dat"): # check that a .dat exists in this folder and matches the directory name
                    os.chdir(os.path.abspath(dirName))
                    xmlfile = glob.glob("*xml")

                    checkShankDirsExist(subdirList,dirName,numShanks,xmlfile) # check if shank dirs exist and make them if they don't

                    for root, shankdirs, defaultFiles in os.walk(dirName):
                        for shank in shankdirs:  # iterate through shank subdirectories
                            # if the shank hasn't already been clustered
                            if not fnmatch.fnmatch(shank, '_klust*'):
                                os.chdir(shank) # now in shank directory
                                for file in os.listdir('.'):
                                    if fnmatch.fnmatch(file, '*.prm'): # double check there's a prm file
                                        checkJobLimits(cpuLimit,numJobs,waittime) # you shall not pass... until other jobs have finished.
                                        if not any(fnmatch.fnmatch(i, '*.kwik') for i in os.listdir('.')): # check that spike extraction hasn't been done
                                            startJob(root,file)
                                        if any(fnmatch.fnmatch(i, 'nohup.out') for i in os.listdir('.')): # check if there is a log file 
                                            status = getFolderStatus();
                                            if any(fnmatch.fnmatch(status, p) for p in ['abandoning', 'finishing']) and not os.path.exists("autoclustering.out"):    
                                                # check Klustakwik has finished
                                                print(os.getcwd())
                                                print('starting autoclustering on ' + shank + ' ..')
                                                with open("autoclustering.out", "wb") as myfile:
                                                    myfile.write("autoclustering in progress\n")
                                                runAutoClust = ['matlab -nodesktop -r "addpath(genpath(' + repoPath + '));'\
                                                ' ; AutoClustering(\'' + dirName.split('/')[-1] + '\', ' + shank + ');exit"']
                                                subprocess.check_call(runAutoClust, shell=True) # making this a check_call forces matlab to complete before going to the next job (only one autoclustering job runs at a time)
                                                # run Autoclustering
                                            if fnmatch.fnmatch(status,'autoclustered') and socket.gethostname() == 'hyperion' and os.path.exists("autoclustering.out"): 
                                                # check that Autoclustering is done
                                                print('copying ' + root + '/' + shank +  ' to SSD and removing progress logfile..')
                                                os.remove("autoclustering.out")
                                                shutil.copytree(root + '/' + shank,'/home/david/to_cut/autoclustered/' + \
                                                    root.split('/')[-2] + '/' + root.split('/')[-1] + '/' + shank)
                                                # copy files to SSD
                                                with open("nohup.out", "a") as myfile:
                                                    myfile.write("copied to SSD\n")
                                                # edit nohup.out to new status
                                os.chdir('..')
                                # return to recording directory
        time.sleep(waittime)

def getCurrentJobs():
    detekt = "phy"
    kk = "klustakwik"
    klusta = "klusta"
    KK = "Klustakwik"  # upper case version on the servers
    matlab = "MATLAB"
    count = 0
    for proc in psutil.process_iter():
        if proc.name() == kk:
            count += 1
        if proc.name() == detekt:
            count += 1
        if proc.name() == klusta:
            count += 1
        if proc.name() == KK:
            count += 1
        if proc.name() == matlab:
            count += 1
    return count

def getFolderStatus():
    with open('nohup.out', "rb") as f:
        if os.path.getsize('nohup.out') > 200:  # checks that file has more than 1 byte written to it
            f.seek(-2, 2)             # Jump to the second last byte.
            while f.read(1) != "\n": # Until EOL is found...
                f.seek(-2, 1)         # ...jump back the read byte plus one more.
            last = f.readline()       # Read last line.
            status = last.split(" ")[-1].split(".")[0]
        else:
            status = ''
    return status

def checkJobLimits(cpuLimit,numJobs,waittime):
    cpu = psutil.cpu_percent(2)
    while cpu > cpuLimit:
        print('current cpu usage: %f' % cpu)
        # wait until resources are available
        time.sleep(waittime)
        cpu = psutil.cpu_percent(2)
    mem = psutil.virtual_memory()  # samples virtual memory usage
    while mem.percent > 90:
        print('current memory usage: %f' % mem.percent)
        # wait until resources are
        # available
        time.sleep(waittime)
        mem = psutil.virtual_memory()
    while getCurrentJobs() >= numJobs:
        print('waiting for %f jobs to finish...' % getCurrentJobs())
        time.sleep(waittime)

def checkShankDirsExist(subdirList,dirName,numShanks,xmlfile):
    subdirList=[d for d in subdirList if not '201' in d if not \
                'extras' in d if not 'temp' in d] # removes folders that are not shank folders
    if len(subdirList) < numShanks:
        # this section needs to be abtracted to the number of
        # shanks instead of a hard number...
        print(os.path.abspath(dirName))
        matlab_command = ['matlab -nodesktop -r "addpath(genpath(\'/zpool/Dropbox/code\')); \
            makeProbeMap(\'' + os.path.abspath(dirName) + '\',\'' + xmlfile[0] + '\');exit"']
        # generate folder structure and .prm/.prb files
        subprocess.call(matlab_command[0], shell=True)
        time.sleep(10)  # let the process get going...
    return True

def checkBehaviorTracking():
    # checks if there is behavioral tracking data that needs to be synced to ephys data
    # eventually this will call Process_ConvertOptitrack2Pos.m or it's replacement
    print()

def startJob(root,file):  # starts the spike extraction/clustering process using
    toRun = ['nohup klusta ' + file + ' &'] # create the klusta command to run
    # run klusta job
    subprocess.call(toRun[0], shell=True)
    # add something here to write the computer name to the log file
    f = open('complog.log', 'w')
    f.write(socket.gethostname())
    f.close()
    print(['starting... ' + root +  toRun[0]])
    time.sleep(10) # let one process start before generating another 

def copyToSSD(ssdCompName,root,shank,status): # copies finished shanks to a SSD for manual spike sorting
    if fnmatch.fnmatch(status,'autoclustered') and socket.gethostname() == 'hyperion' and os.path.exists("autoclustering.out"): 
        # check that Autoclustering is done
        print('copying ' + root + '/' + shank +  ' to SSD and removing progress logfile..')
        os.remove("autoclustering.out")
        shutil.copytree(root + '/' + shank,'/home/david/to_cut/autoclustered/' + \
        root.split('/')[-2] + '/' + root.split('/')[-1] + '/' + shank)
        # copy files to SSD
        with open("nohup.out", "a") as myfile:
            myfile.write("copied to SSD\n")

if __name__ == "__main__":
    main(sys.argv[1:])
