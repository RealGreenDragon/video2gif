@echo off

REM ----- VARS -----

SET in_mp4=big_buck_bunny_720p_30mb.mp4
SET in_mkv=big_buck_bunny_720p_30mb.mkv

SET in_srt=test_sub.srt
SET in_ass=test_sub.ass

SET start=00:00:43.900
SET end=00:00:48.100

SET out_mp4_nosub=out_mp4_nosub.gif
SET out_mp4_srt=out_mp4_srt.gif
SET out_mp4_ass=out_mp4_ass.gif

SET out_mkv_nosub=out_mkv_nosub.gif
SET out_mkv_srt=out_mkv_srt.gif
SET out_mkv_ass=out_mkv_ass.gif

SET log_mp4_nosub=log_mp4_nosub.txt
SET log_mp4_srt=log_mp4_srt.txt
SET log_mp4_ass=log_mp4_ass.txt

SET log_mkv_nosub=log_mkv_nosub.txt
SET log_mkv_srt=log_mkv_srt.txt
SET log_mkv_ass=log_mkv_ass.txt


REM ----- MP4 TESTS -----

echo.
echo #### MP4 No Sub ####
python -B ..\src\video2gif.py "%in_mp4%" "%out_mp4_nosub%" -l verbose -a %start% -t %end% -m diff 2> %log_mp4_nosub%

echo.
echo #### MP4 SRT ####
python -B ..\src\video2gif.py "%in_mp4%" "%out_mp4_srt%" -l verbose -a %start% -t %end% -m diff --burn-sub-file %in_srt% 2> %log_mp4_srt%

echo.
echo #### MP4 ASS ####
python -B ..\src\video2gif.py "%in_mp4%" "%out_mp4_ass%" -l verbose -a %start% -t %end% -m diff --burn-sub-file %in_ass% 2> %log_mp4_ass%


REM ----- MKV TESTS -----

echo.
echo #### MKV No Sub ####
python -B ..\src\video2gif.py "%in_mkv%" "%out_mkv_nosub%" -l verbose -a %start% -t %end% -m diff 2> %log_mkv_nosub%

echo.
echo #### MKV SRT ####
python -B ..\src\video2gif.py "%in_mkv%" "%out_mkv_srt%" -l verbose -a %start% -t %end% -m diff --burn-sub-track 1 2> %log_mkv_srt%

echo.
echo #### MKV ASS ####
python -B ..\src\video2gif.py "%in_mkv%" "%out_mkv_ass%" -l verbose -a %start% -t %end% -m diff --burn-sub-track 0 2> %log_mkv_ass%

pause
