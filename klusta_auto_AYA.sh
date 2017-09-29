#!/bin/bash
#$ -S /bin/bash
#$ -cwd

echo ${DATAFOLDER}
#echo ${FILE}
echo ${SHANK}
echo ${RECORDING}

module load metaseq









source activate klusta

klusta ${DATAFOLDER}/${SHANK}/${RECORDING}
