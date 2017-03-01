# ephys-processing-pipeline

This is a set of tools used for the semi-automated processing of raw ephys recording data.  Things included here:

-spike extraction (spikedetekt)
-automated spike sorting (klusta-3.0)
-LFP downsampling and extraction (TODO)
-synchronization of behavioral tracking data and ephys data (https://github.com/buzsakilab/buzcode)


INSTALL

`cd ephys-processing-pipeline/installation`

`./install`

Yes and enter to all queries


HOW TO RUN PIPELINE

run from within /ephys-processing-pipeline folder
`python processRecordings.py /path/to/recording/folder numShanks`

usage: processRecordings.py [-h] [-waitTime WAITTIME] [-numJobs NUMJOBS]
                            [-cpuLimit CPULIMIT] [-repoPath REPOPATH]
                            dataFolder numShanks

This function is designed to run in the background on a data processing
machine. It constantly searches through a given directory [arg1] and starts
extract, clustering, and other processing jobs

positional arguments:
  dataFolder          the folder with all of your recordings in subdirectories
  numShanks           number of shanks to process

optional arguments:
  -h, --help          show this help message and exit
  -waitTime WAITTIME  time (seconds) to wait before searching for more jobs
                      [default = 300]
  -numJobs NUMJOBS    number of jobs to run simultaneously [default = 4]
  -cpuLimit CPULIMIT  cpu usage limit [default = 80]
  -repoPath REPOPATH  location of ephys-processing repository