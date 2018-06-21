ECHO OFF
ECHO "Extracting Feature points from '%1'..."

SET FFMPEG_PATH="C:\port\ffmpeg\bin\ffmpeg.exe"

%FFMPEG_PATH% -i "%1" -filter:v "select='eq(pict_type\,I)" ^
-vf "drawtext=fontfile='C\:\\Windows\\Fonts\\Consolas.ttf':text='\%%H:\%%M:\%%S':^
fontcolor=0xFFFFFFFF:fontsize=12^
x=10:h-th-10:" -vsync vfr "%1_th_%%02d.jpg"