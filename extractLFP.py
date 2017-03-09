#!/home/david/miniconda/envs/klusta/bin/python

import numpy as np
import scipy as sp
import scipy.signal as sig
import argparse
import os
import matplotlib.pyplot as plt

# def sinc_interp(x, s, u):
#     """
#     Interpolates x, sampled at "s" instants
#     Output y is sampled at "u" instants ("u" for "upsampled")
    
#     from Matlab:
#     http://phaseportrait.blogspot.com/2008/06/sinc-interpolation-in-matlab.html        
#     """
    
#     if len(x) != len(s):
#         raise Exception, 'x and s must be the same length'
    
#     # Find the period    
#     T = s[1] - s[0]
    
#     sincM = np.tile(u, (len(s), 1)) - np.tile(s[:, np.newaxis], (1, len(u)))
#     y = np.dot(x, np.sinc(sincM/T))
#     return y

def main(args):
    # check here and remove/rename old lfp files?

    # start
    dataFolder = args.dataFolder
    inputFile = args.inputFile
    outputFile = args.outputFile
    nChannels = args.nChannels

    chunkSize = 20000
    inputFile = dataFolder + '/' + inputFile
    recordingSize = float(os.path.getsize(inputFile))

    fid = open(inputFile, 'r')
    outputFile = dataFolder + '/' + outputFile
    out = open(outputFile, 'w')

    a = np.fromfile(fid, count=chunkSize*nChannels, dtype=np.int16)
    counter = 0;
    fWindow = sig.get_window('hamming',1)

    while a.size > 1:
        lfp = a.reshape(nChannels,chunkSize,order='F')
        lfp_down = np.ndarray((nChannels,1250))
        # plt.subplot(211)
        # plt.plot(np.transpose(lfp))
        for i in range(0,nChannels,1):
            lfp_down[i,:] = sig.resample_poly(lfp[i,:],1250,chunkSize,window=fWindow)
            # lfp_down[i,:] = sinc_interp(lfp[i,:],np.arange(0,1,1/20000.),np.arange(0,1,1/1250.))
        #     plt.subplot(212)
        #     plt.plot(np.transpose(lfp_down))
        # plt.show()
        b = lfp_down.reshape(nChannels*1250,1,order='F')
        # plt.subplot(211)
        # plt.plot(b[1:1250])
        # plt.subplot(212)
        # plt.plot(a[1:20000])
        # plt.show()
        # out.write(np.transpose(np.int16(b)))
        np.transpose(np.int16(b)).tofile(out)
        a = np.fromfile(fid, count=chunkSize*nChannels, dtype=np.int16)
        if counter % 60 == 0:
            print(['extracting LFP: ' + str((counter*chunkSize*nChannels)/recordingSize) + ' percent done...'])
        counter = counter + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This function is designed to extract a *.lfp'
                                     'file from a *.dat file given')
    parser.add_argument('dataFolder', type=str, default=os.getcwd(), help='the folder with all of your recordings in subdirectories')
    parser.add_argument('nChannels', type=np.int16, default=1, help='the number of channels')
    parser.add_argument('inputFile', type=str, default='amplifier.dat', help='input .dat file')
    parser.add_argument('-outputFile', type=str, default='amplifier.lfp', help='output .lfp file [default = inputFile.lfp]')
    # parser.add_argument('-numJobs',type=float,default=4,help='number of jobs to run simultaneously [default = 4]')
    # parser.add_argument('-cpuLimit',type=float,default=80,help='cpu usage limit [default = 80]')
    # parser.add_argument('-repoPath',type=str,default=sys.argv[0],help='location of ephys-processing repository')
    args = parser.parse_args()
    print(args)
    main(args)

