#!/home/david/miniconda/envs/klusta/bin/python

import numpy as np
import scipy as sp


def main():
    dataFolder = args.dataFolder
    inputFile = args.inputFile
    outputFile = args.outputFile
    nChannels = args.nChannels

    chunkSize = 20000
    fid = open([dataFolder + '/' + inputFile, 'r'])
    out = open([dataFolder + '/' + outputFile, 'w'])


    a = np.fromfile(fid, count=chunkSize*nChannels, dtype=np.int16)

    lfp = a.reshape(nChannels,chunkSize)
    lfp_down = np.ndarray((nChannels,1250))
    for i in range(0,nChannels,1):
        lfp_down[i,:] = sp.signal.resample(lfp[i,:],1250)

    b = lfp_down.reshape(nChannels*chunkSize,1)
    b.tofile(out)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This function is designed to extract a *.lfp'
                                     'file from a *.dat file given')
    parser.add_argument('dataFolder', type=str, default=os.getcwd(), help='the folder with all of your recordings in subdirectories')
    parser.add_argument('nChannels', type=np.int16, default=1, help='the number of channels')
    parser.add_argument('inputFile', type=str, default='amplifier.dat', help='input .dat file')
    parser.add_argument('-outputFile', type=str, default='amplifier.dat', help='output .lfp file [default = inputFile.lfp]')
    # parser.add_argument('-numJobs',type=float,default=4,help='number of jobs to run simultaneously [default = 4]')
    # parser.add_argument('-cpuLimit',type=float,default=80,help='cpu usage limit [default = 80]')
    # parser.add_argument('-repoPath',type=str,default=sys.argv[0],help='location of ephys-processing repository')
    args = parser.parse_args()
    print(args)
    main(args)
