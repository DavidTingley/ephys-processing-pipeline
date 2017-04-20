#!/home/david/miniconda/envs/klusta/bin/python

import numpy as np
import scipy.signal as sig
import argparse
import os

def main(dataFolder,inputFile,outputFile,nChannels,inChunkSize,outChunkSize):
    # parse args

    inputFile = dataFolder + '/' + inputFile
    recordingSize = int(os.path.getsize(inputFile))

    fid = open(inputFile, 'r')
    outputFile = dataFolder + '/' + outputFile
    out = open(outputFile, 'w')

    a = np.fromfile(fid, count=inChunkSize*nChannels, dtype=np.int16)
    counter = 0;
    # fWindow = sig.get_window(('gaussian',10000./500.),20)
    fWindow = sig.kaiser(2,010000./500.)
    # bb, aa = sig.cheby2(256,40,500./10000.,'lowpass')
    # fWindow = sig.firwin(3,500.,window='chebwin',100.,nyq=10000.)

    while a.size > 1:
        try: # if len(a) == chunkSize*nChannels?
            lfp = a.reshape(nChannels,inChunkSize,order='F')
        except: # elseif len(a) < chunkSize*nChannels?
            lastChunk = a.size / nChannels # re-assign chunkSize for the last chunk of data
            outChunkSize = lastChunk / (inChunkSize / outChunkSize)
            print(lastChunk, outChunkSize)
            lfp = a.reshape(nChannels,lastChunk,order='F')
            inChunkSize = lastChunk  # overwrite inChunk with lastChunk size
            
        lfp_down = np.ndarray((nChannels,outChunkSize))

        for i in range(0,nChannels,1):
            lfp_down[i,:] = sig.resample_poly(lfp[i,:],outChunkSize,inChunkSize,window=fWindow)

        b = lfp_down.reshape(nChannels*outChunkSize,1,order='F')
        np.transpose(np.int16(b)).tofile(out)
        a = np.fromfile(fid, count=inChunkSize*nChannels, dtype=np.int16)
        if counter % 360 == 0:
            print(['extracting LFP: ' + str(200*(counter*inChunkSize*nChannels)/recordingSize) + ' percent done...'])
        counter = counter + 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This function is designed to extract a *.lfp'
                                     'file from a *.dat file given')
    parser.add_argument('dataFolder', type=str, default=os.getcwd(), help='the folder with all of your recordings in subdirectories')
    parser.add_argument('nChannels', type=np.int16, default=1, help='the number of channels')
    parser.add_argument('inputFile', type=str, default='amplifier.dat', help='input .dat file')
    parser.add_argument('-outputFile', type=str, default='amplifier.lfp', help='output .lfp file [default = inputFile.lfp]')
    parser.add_argument('-inSamplingRate', type=int, default=20000, help='sampling rate of the recording [default = 20000]')
    parser.add_argument('-outSamplingRate', type=int, default=1250, help='desired sampling rate of LFP file [default = 1250]')
    args = parser.parse_args()
    # check here and remove/rename old lfp files?

    # start
    main(dataFolder = args.dataFolder,
    inputFile = args.inputFile,
    outputFile = args.outputFile,
    nChannels = args.nChannels,
    inChunkSize = args.inSamplingRate,
    outChunkSize = args.outSamplingRate)

