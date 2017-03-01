#!/home/david/miniconda/envs/klusta/bin/python

import psutil
import time
import subprocess
import os
import glob
import fnmatch
import socket
import shutil
import argparse

# TODO
# - add behavior tracking extraction
# - add LFP extraction
# - add SSD copying functionality
ssdDirectory = '/home/david/to_cut/autoclustered/'
ssdCompName = 'hyperion'

def main(args):
    dataFolder = args.dataFolder # directory with recording subdirectories
    numShanks = args.numShanks# set this value to the number of shanks (spike groups) to cluster
    waitTime = args.waitTime # time interval, in seconds, in between starting new extraction/clustering jobs
    numJobs = args.numJobs# max number of jobs to run at once
    cpuLimit = args.cpuLimit  # max cpu usage allowed before starting new jobs
    repoPath = args.repoPath

    print('repo path is : ' + repoPath)

    while True:  # this is the song that never ends....
        os.chdir(dataFolder)
        print('searching for unprocessed recordings...')
        for dirName, subdirList, fileList in os.walk(dataFolder):
            for file in fileList:
                # check that a .dat exists in this folder and matches the
                # directory name
                if file.startswith(dirName.split('/')[-1]) & file.endswith(".dat"):
                    os.chdir(os.path.abspath(dirName))
                    xmlfile = glob.glob("*xml")
                    # check if shank dirs exist and make them if they don't
                    checkShankDirsExist(subdirList, dirName, numShanks, xmlfile,repoPath)
                    for root, shankdirs, defaultFiles in os.walk(dirName):
                        for shank in shankdirs:  # iterate through shank subdirectories
                            # if the shank hasn't already been clustered and its directory name is less than 3 characters
                            if not fnmatch.fnmatch(shank, '_klust*') and len(shank) < 3:
                                os.chdir(shank)  # now in shank directory
                                for file in os.listdir('.'):
                                    # double check there's a prm file
                                    if fnmatch.fnmatch(file, '*.prm'):
                                        # you shall not pass... until other
                                        # jobs have finished.
                                        checkJobLimits(cpuLimit, numJobs, waitTime)
                                        # check that spike extraction hasn't
                                        # been done
                                        if not any(fnmatch.fnmatch(i, '*.kwik') for i in os.listdir('.')):
                                            startClusterJob(root, file)
                                        # check if there is a log file
                                        if any(fnmatch.fnmatch(i, 'nohup.out') for i in os.listdir('.')):
                                            status = getFolderStatus()
                                            startAutoClustering(shank, dirName,repoPath,status)
                                            copyToSSD(
                                                ssdCompName, ssdDirectory, root, shank, status)
                                os.chdir('..')  # return to recording directory
        time.sleep(waitTime)  # it goes on and on my friends...


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
        if os.path.getsize('nohup.out') > 200: # checks that file has more than 1 byte written to it
            f.seek(-2, 2)             # Jump to the second last byte.
            while f.read(1) != "\n":  # Until EOL is found...
                # ...jump back the read byte plus one more.
                f.seek(-2, 1)
            last = f.readline()       # Read last line.
            status = last.split(" ")[-1].split(".")[0]
        else:
            status = ''
    return status


def checkJobLimits(cpuLimit, numJobs, waitTime):
    cpu = psutil.cpu_percent(2)
    while cpu > cpuLimit:
        print('current cpu usage: %f' % cpu)
        # wait until resources are available
        time.sleep(waitTime)
        cpu = psutil.cpu_percent(2)
    mem = psutil.virtual_memory()  # samples virtual memory usage
    while mem.percent > 90:
        print('current memory usage: %f' % mem.percent)
        # wait until resources are
        # available
        time.sleep(waitTime)
        mem = psutil.virtual_memory()
    while getCurrentJobs() >= numJobs:
        print('waiting for %f jobs to finish...' % getCurrentJobs())
        time.sleep(waitTime)


def checkShankDirsExist(subdirList, dirName, numShanks, xmlfile,repoPath):
    try:
        subdirList = [d for d in subdirList if not '201' in d if not
                      'extras' in d if not 'temp' in d]  # removes folders that are not shank folders
        if len(subdirList) < numShanks:
            # this section needs to be abtracted to the number of
            # shanks instead of a hard number...
            print(os.path.abspath(dirName))
            matlab_command = ['matlab -nodesktop -r "addpath(genpath(\'' + repoPath + '\')); \
                makeProbeMap(\'' + os.path.abspath(dirName) + '\',\'' + xmlfile[0] + '\');exit"']
            # generate folder structure and .prm/.prb files
            subprocess.call(matlab_command[0], shell=True)
            time.sleep(10)  # let the process get going...
        return True
    except:
        print('errorrr')
        return False


def extractBehaviorTracking():
    # checks if there is behavioral tracking data that needs to be synced to ephys data
    # eventually this will call Process_ConvertOptitrack2Behav.m or it's
    # replacement
    print('this function is currently empty....')

def extractLFP():
    # extracts LFP from raw *.dat file and saves to current directory
    print('this function is currently empty....')


def startClusterJob(root, file):  # starts the spike extraction/clustering process using
    toRun = ['nohup klusta ' + file + ' &']  # create the klusta command to run
    # run klusta job
    subprocess.call(toRun[0], shell=True)
    # add something here to write the computer name to the log file
    f = open('complog.log', 'w')
    f.write(socket.gethostname())
    f.close()
    print(['starting... ' + root + toRun[0]])
    time.sleep(10)  # let one process start before generating another


def startAutoClustering(shank, dirName,repoPath,status):
    if any(fnmatch.fnmatch(status, p) for p in ['abandoning', 'finishing']) and not os.path.exists("autoclustering.out"):
        # check Klustakwik has finished
        print(os.getcwd())
        print('starting autoclustering on ' + shank + ' ..')
        with open("autoclustering.out", "wb") as myfile:
            myfile.write("autoclustering in progress\n")
        runAutoClust = ['matlab -nodesktop -r "addpath(genpath(\'' + repoPath + '\'));'
                        ' AutoClustering(\'' + dirName.split('/')[-1] + '\', ' + shank + ');exit"']
        # making this a check_call forces matlab to complete before going to
        # the next job (only one autoclustering job runs at a time)
        subprocess.check_call(runAutoClust, shell=True)



def copyToSSD(ssdCompName, ssdDirectory, root, shank, status): # copies finished shanks to a SSD for manual spike sorting
    if fnmatch.fnmatch(status, 'autoclustered') and socket.gethostname() == 'hyperion' and os.path.exists("autoclustering.out"):
        # checks that Autoclustering is done
        print('copying ' + root + '/' + shank +
              ' to SSD and removing progress logfile..')
        os.remove("autoclustering.out")
        shutil.copytree(root + '/' + shank, ssdDirectory +
                        root.split('/')[-2] + '/' + root.split('/')[-1] + '/' + shank)
        # copy files to SSD
        with open("nohup.out", "a") as myfile:
            myfile.write("copied to SSD\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This function is designed to run '\
                                         'in the background on a data processing '\
                                         'machine.  It constantly searches through '\
                                         'a given directory [arg1] and starts extract,'\
                                         ' clustering, and other processing jobs')
    parser.add_argument('dataFolder',type=str,default=os.getcwd(),help='the folder with all of your recordings in subdirectories')
    parser.add_argument('numShanks',type=float,default=10,help='number of shanks to process')
    parser.add_argument('-waitTime',type=int,default=300,help='time (seconds) to wait before searching for more jobs [default = 300]')
    parser.add_argument('-numJobs',type=float,default=4,help='number of jobs to run simultaneously [default = 4]')
    parser.add_argument('-cpuLimit',type=float,default=100,help='cpu usage limit [default = 80]')
    parser.add_argument('-repoPath',type=str,default=os.getcwd(),help='location of ephys-processing repository')
    args = parser.parse_args()
    main(args)
