ECHO Concatinating video '%1' to h264/mp3 in a .mp4 wrapper

SET FFMPEG_PATH="C:\port\ffmpeg\bin\ffmpeg.exe"
SET FFMPEG_CMD=-filter_complex "[0:a:0][0:a:1]amerge" -c:v libx264 -preset faster -crf 26 -c:a mp3

%FFMPEG_PATH% -i "%1" %FFMPEG_CMD% "%~dpn1.mp4"