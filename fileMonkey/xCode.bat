ECHO "Transcoding '%1' to '%2'"
SET FFMPEG_PATH="C:\port\ffmpeg\bin\ffmpeg.exe"
FOR /F "tokens=*" %%G IN ('dir /b %1') DO %FFMPEG_PATH% -i "%%G" -c:v libx264 -preset slow -crf 22 -c:a copy "%%~nG%2"