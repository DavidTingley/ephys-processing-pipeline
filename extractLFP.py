#!/home/david/miniconda/envs/klusta/bin/python

import numpy as np
import scipy.signal as sig
import argparse
import os

def main(args):
    # check here and remove/rename old lfp files?

    # start
    dataFolder = args.dataFolder
    inputFile = args.inputFile
    outputFile = args.outputFile
    nChannels = args.nChannels
    chunkSize = args.recSamplingRate
    lfpChunk = args.lfpSamplingRate
    
    inputFile = dataFolder + '/' + inputFile
    recordingSize = int(os.path.getsize(inputFile))

    fid = open(inputFile, 'r')
    outputFile = dataFolder + '/' + outputFile
    out = open(outputFile, 'w')

    a = np.fromfile(fid, count=chunkSize*nChannels, dtype=np.int16)
    counter = 0;
    fWindow = sig.get_window('hamming',1)

    while a.size > 1:
        try: # if len(a) == chunkSize*nChannels?
            lfp = a.reshape(nChannels,chunkSize,order='F')
        except: # elseif len(a) < chunkSize*nChannels?
            chunkSize = a.size / nChannels # re-assign chunkSize for the last chunk of data
            lfpChunk = chunkSize / 16
            print(chunkSize, lfpChunk)
            lfp = a.reshape(nChannels,chunkSize,order='F')
            
        lfp_down = np.ndarray((nChannels,lfpChunk))

        for i in range(0,nChannels,1):
            lfp_down[i,:] = sig.resample_poly(lfp[i,:],lfpChunk,chunkSize,window=fWindow)

        b = lfp_down.reshape(nChannels*lfpChunk,1,order='F')
        np.transpose(np.int16(b)).tofile(out)
        a = np.fromfile(fid, count=chunkSize*nChannels, dtype=np.int16)
        if counter % 360 == 0:
            print(['extracting LFP: ' + str(200*(counter*chunkSize*nChannels)/recordingSize) + ' percent done...'])
        counter = counter + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This function is designed to extract a *.lfp'
                                     'file from a *.dat file given')
    parser.add_argument('dataFolder', type=str, default=os.getcwd(), help='the folder with all of your recordings in subdirectories')
    parser.add_argument('nChannels', type=np.int16, default=1, help='the number of channels')
    parser.add_argument('inputFile', type=str, default='amplifier.dat', help='input .dat file')
    parser.add_argument('-outputFile', type=str, default='amplifier.lfp', help='output .lfp file [default = inputFile.lfp]')
    parser.add_argument('-recSamplingRate', type=int, default=20000, help='sampling rate of the recording [default = 20000]')
    parser.add_argument('-lfpSamplingRate', type=int, default=1250, help='desired sampling rate of LFP file [default = 1250]')
    
    args = parser.parse_args()
    main(args)

