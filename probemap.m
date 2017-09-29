function [] = probemap(DATAFOLDER,RECORDING,SHANK)

addpath(genpath('/ifs/home/dwt244/buzcode'));
addpath(genpath('/ifs/home/dwt244/ephys-processing-pipeline'));
makeProbeMap_phoenix;

end
