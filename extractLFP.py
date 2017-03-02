import numpy as np


def main():
    dataFolder = args.dataFolder
    inputFile = args.inputFile
    outputFile = args.outputFile
    chunkSize = 20000
    fid = open([dataFolder + '/' + inputFile, 'r'])
    a = np.fromfile(fid, dtype=np.int16)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This function is designed to extract a *.lfp'
                                     'file from a *.dat file given')
    parser.add_argument('dataFolde', type=str, default=os.getcwd(), help='the folder with all of your recordings in subdirectories')
    parser.add_argument('inputFile', type=str, default='amplifier.dat', help='input .dat file')
    parser.add_argument('-outputFile', type=str, default='amplifier.dat', help='output .lfp file [default = inputFile.lfp]')
    # parser.add_argument('-numJobs',type=float,default=4,help='number of jobs to run simultaneously [default = 4]')
    # parser.add_argument('-cpuLimit',type=float,default=80,help='cpu usage limit [default = 80]')
    # parser.add_argument('-repoPath',type=str,default=sys.argv[0],help='location of ephys-processing repository')
    args = parser.parse_args()
    print(args)
    main(args, sys)
