ECHO OFF
ECHO Concatinating vids '%1' to h264/mp3 in a .mp4 wrapper

SET FFMPEG_PATH="C:\port\ffmpeg\bin\ffmpeg.exe"
SET FFMPEG_CMD=-filter_complex "[0:a:0][0:a:1]amerge" -c:v libx264 -preset faster -crf 26 -c:a mp3

FOR %%f in ( %1 ) do (
    ECHO file '%%f' >> files.txt
    IF "%%G"=="" SET G=%%f
)
ECHO ON
%FFMPEG_PATH% -f concat -i files.txt %FFMPEG_CMD% "%%~nG.mp4"

DEL files.txt