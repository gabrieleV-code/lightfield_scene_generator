%filePattern = fullfile('C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_Padded_001\Lenslets', 'untitled_7.jpg');
%filePattern = 'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\Networks_Italo\Data\EPFL_16Lenslets';
filePattern = 'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_001\LFs\LF_Scene_00\lf_1\LFPlane.001\png_cut_13'
theFiles = dir(filePattern);
theFiles = theFiles(3:20,:);
brisque_tot=0;
sharpness_tot = 0;
for k = 1:length(theFiles)
    baseFileName = theFiles(k).name;
    fullFileName = fullfile(theFiles(k).folder, baseFileName);
    %fprintf(1, 'Now reading %s\n', fullFileName);
    % Now do whatever you want with this file name,
    % such as reading it in as an image array with imread()
    imageArray = imread(fullFileName);
    %imshow(imageArray);  % Display image.
    %drawnow; % Force display to update immediately.
    brisque_ = brisque(imageArray);
    %fprintf('Brisque %f\n', brisque_);
    brisque_tot = brisque_+brisque_tot;
%     sharpness_ = measureSharpness(imageArray);
%     sharpness_tot = sharpness_ + sharpness_tot
end

brisque_tot/length(theFiles)
sharpness_tot/length(theFiles)

