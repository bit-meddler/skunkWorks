ECHO OFF
ECHO "Transcoding '%1' to h264 in a '%2'"

SET FFMPEG_PATH="C:\port\ffmpeg\bin\ffmpeg.exe"
SET FFMPEG_CMD="-c:v libx264 -preset slow -crf 22 -c:a copy"

FOR /F "tokens=*" %%G IN ('dir /b %1') DO (
    %FFMPEG_PATH% -i "%%G" %FFMPEG_CMD% "%%~nG%2"
)