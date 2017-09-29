#!/bin/bash
#$ -S /bin/bash
#$ -cwd

echo ${DATAFOLDER}
echo ${RECORDING}
echo ${SHANK}


module load metaseq
source activate klusta

klusta ${DATAFOLDER}/${RECORDING}/${SHANK}/${RECORDING}_sh${SHANK}.prm
