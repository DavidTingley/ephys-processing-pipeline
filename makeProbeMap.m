function [] = makeProbeMap(folder, xmlfile)
%% this function takes an xml file with spike groups already assigned and
%% generates *.prb files for each shank for spike detection/masking/clustering

%% IMPORTANT: this function ASSUMES that the order of the channels for each shank
%% in the spike groups map onto a specific geometrical arrangement of channels on the shank
%% starting from the top left recording site, and moving right then downward to make the
%% nearest neighbor graph

parameters = LoadParameters([folder]);
% warning off

for shank = 1:parameters.spikeGroups.nGroups
    % make a folder for each directory
    try
        if ~exist([folder '/' num2str(shank)])
            disp(['working on spike group #' num2str(shank)])
            mkdir([folder '/' num2str(shank)]);
            
            channels = parameters.spikeGroups.groups{shank};
            c=1;
            for i=1:length(channels)-1
                for j=1
                    l(c,:) = [channels(i),channels(i+j)];
                    c=1+c;
                end
            end
            if length(channels) < 32
                for i=1:length(channels)-2
                    for j=2
                        l(c,:) = [channels(i),channels(i+j)];
                        c=1+c;
                    end
                end
                for i=1:length(channels)-3
                    for j=3
                        l(c,:) = [channels(i),channels(i+j)];
                        c=1+c;
                    end
                end
            end
            list = l;
            
            
            s=['channel_groups = {\n' num2str(shank) ': {\n'];
            
            s=[s, '\t"channels": [\n' ];
            for i =1:length(channels)-1
                s=[s, '' num2str(channels(i)) ', ' ];
            end
            s=[s, '' num2str(channels(i+1))];
            s=[s, '],\n' ];
            
            s=[s, '\t"graph": [\n' ];
            for i =1:length(list)-1
                s=[s, '\t(' num2str(list(i,1)) ', ' num2str(list(i,2)) '),\n'];
            end
            %     s=[s, '\t(' num2str(list(i+1,1)) ', ' num2str(list(i+1,2)) ')\n'];
            s=[s, '\t],\n' ];
            
            s=[s, '\t"geometry": {\n' ];
            for i =1:length(channels)
                if mod(i,2)
                    pn = -1;
                else
                    pn = 1;
                end
                %     s=[s, '\t' num2str(channels(i)) ': [' num2str(pn*(-(20+1-i)*2)) ', ' num2str(-i*10) '], \n'];
                s=[s, '\t' num2str(channels(i)) ': [' num2str(pn*20) ', ' num2str(-i*10) '], \n'];
            end
            s=[s, '\t},\n},\n}' ];
            
            % write .prb files to each shank folder
            fid = fopen([folder '/' num2str(shank) '/' num2str(shank) '.prb'],'wt');
            fprintf(fid,s);
            fclose(fid);
            
            % write .prm file as well
            fid = fopen('generic_spikedetekt.prm');
            i = 1;
            tline = fgetl(fid);
            generic{i} = tline;
            while ischar(tline)
                i = i+1;
                tline = fgetl(fid);
                generic{i} = tline;
            end
            fclose(fid);
            % change the location of the *.dat file in the *.prm file
            %     generic{4} = ;
            fid = fopen([folder '/' num2str(shank) '/' parameters.FileName '_sh' num2str(shank) '.prm'],'wt');
            ss = ['EXPERIMENT_NAME = ''' folder '/' num2str(shank) '/' parameters.FileName '_sh' num2str(shank) '''\n',...
                'RAW_DATA_FILES=[''' folder  '/' parameters.FileName '.dat'  ''']\n',...
                'PRB_FILE = ''' num2str(shank) '.prb''\n',...
                'NCHANNELS = ' num2str(parameters.nChannels) '\n',...
                'sample_rate = ' num2str(parameters.rates.wideband) '.\n',...
                'NBITS = ' num2str(parameters.nBits) '\n'];
            
            fprintf(fid,ss);
            for i = 1:numel(generic)
                if generic{i+1} == -1
                    fprintf(fid,'%s', generic{i});
                    break
                else
                    fprintf(fid,'%s\n', generic{i});
                end
            end
            clear s l list c ss
        end
    catch
        warning(['did not work correctly for spike group ' shank]);
    end
end

