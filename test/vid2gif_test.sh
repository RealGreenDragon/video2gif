#!/bin/bash


# ----- VARS -----

in_mp4=big_buck_bunny_720p_30mb.mp4
in_mkv=big_buck_bunny_720p_30mb.mkv

in_srt=test_sub.srt
in_ass=test_sub.ass

start=00:00:43.900
end=00:00:48.100

out_mp4_nosub=out_mp4_nosub.gif
out_mp4_srt=out_mp4_srt.gif
out_mp4_ass=out_mp4_ass.gif

out_mkv_nosub=out_mkv_nosub.gif
out_mkv_srt=out_mkv_srt.gif
out_mkv_ass=out_mkv_ass.gif

log_mp4_nosub=log_mp4_nosub.txt
log_mp4_srt=log_mp4_srt.txt
log_mp4_ass=log_mp4_ass.txt

log_mkv_nosub=log_mkv_nosub.txt
log_mkv_srt=log_mkv_srt.txt
log_mkv_ass=log_mkv_ass.txt


# ----- MP4 TESTS -----

printf '\n#### MP4 No Sub ####\n'
python -B ../src/video2gif.py "$in_mp4" "$out_mp4_nosub" -l verbose -a $start -t $end -m diff 2> $log_mp4_nosub

printf '\n#### MP4 SRT ####\n'
python -B ../src/video2gif.py "$in_mp4" "$out_mp4_srt" -l verbose -a $start -t $end -m diff --burn-sub-file $in_srt 2> $log_mp4_srt

printf '\n#### MP4 ASS ####\n'
python -B ../src/video2gif.py "$in_mp4" "$out_mp4_ass" -l verbose -a $start -t $end -m diff --burn-sub-file $in_ass 2> $log_mp4_ass


# ----- MKV TESTS -----

printf '\n#### MKV No Sub ####\n'
python -B ../src/video2gif.py "$in_mkv" "$out_mkv_nosub" -l verbose -a $start -t $end -m diff 2> $log_mkv_nosub

printf '\n#### MKV SRT ####\n'
python -B ../src/video2gif.py "$in_mkv" "$out_mkv_srt" -l verbose -a $start -t $end -m diff --burn-sub-track 1 2> $log_mkv_srt

printf '\n#### MKV ASS ####\n'
python -B ../src/video2gif.py "$in_mkv" "$out_mkv_ass" -l verbose -a $start -t $end -m diff --burn-sub-track 0 2> $log_mkv_ass
