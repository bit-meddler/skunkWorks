ECHO ON
ECHO "Extracting Feature points from '%1'..."

SET FFMPEG_PATH="C:\port\ffmpeg\bin\ffmpeg.exe"

%FFMPEG_PATH% -i "%1" -vf select=eq(pict_type\,I),drawtext=fontfile='C\:\\Windows\\Fonts\\Consola.ttf':text='%%{pts\:hms}':fontcolor=white:fontsize=22:x=10:y=h-th-10 -vsync vfr "%~n1_if_%%02d.jpg"
%FFMPEG_PATH% -i "%1" -vf select=gt(scene\,0.31),drawtext=fontfile='C\:\\Windows\\Fonts\\Consola.ttf':text='%%{pts\:hms}':fontcolor=white:fontsize=22:x=10:y=h-th-10 -vsync vfr "%~n1_sd_%%02d.jpg"