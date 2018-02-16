# Video To GIF
FFmpeg wrapper to easily create GIFs from videos (also with subtitles).

## Requirements
- Python 2.7.x or 3.x (all you need are in the Python Standard Library)
- Install [FFmpeg](https://www.ffmpeg.org/download.html) v3.4 or upper (or copy in the "src" folder a precompiled version)
- (Optional) Install [Gifsicle](https://www.lcdf.org/gifsicle/) (or copy in the "src" folder a precompiled version) to unlock other functions

## Usage
```
python video2gif.py sourceVideo destinationGif [OPTIONS]

Positional arguments:
  sourceVideo           Source video path
  destinationGif        Output GIF path

Optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -f FPS, --fps FPS     Set the fps. (Default: 15)
  -s SIZE, --size SIZE  GIF size, in WIDTH:HEIGHT format. "0" can be used to
                        keep the ratio ("0:0" keep video size). (Default:
                        640:0)
  -r {lanczos,bicubic,spline16,spline36,point,bilinear}, --resize-mode {lanczos,bicubic,spline16,spline36,point,bilinear}
                        Resize filter, one of
                        (lanczos|bicubic|spline16|spline36|point|bilinear).
                        (Default: lanczos)
  -a START, --at START  Moment in which the GIF begins, in seconds or
                        "HH:MM:SS[.m+]" time format. If setted, must be lower
                        than --to param. (Default: 0)
  -t END, --to END      Moment in which the GIF ends, in seconds or
                        "HH:MM:SS[.m+]" time format. If setted, must be
                        greater than --at param. (Default: Till end)
  -d {bayer,floyd_steinberg,sierra2,sierra2_4a,none}, --dither {bayer,floyd_steinberg,sierra2,sierra2_4a,none}
                        Dithering algorithm to use. One of
                        (bayer|floyd_steinberg|sierra2|sierra2_4a|none).
                        (Default: bayer)
  -b {0,1,2,3,4,5}, --bayer-scale {0,1,2,3,4,5}
                        Select the Bayer algorithm scale factor, in the range
                        [0 - 5] (used only if --dither is "bayer"). Lower
                        values tend to produce less artefacts but larger
                        images. (Default: 2)
  -m {full,diff,single}, --mode {full,diff,single}
                        Color generation mode, one of (full|diff|single).
                        'diff' optimize the colors of moving objects at the
                        cost of the background quality, 'single' optimize the
                        colors for each frame (but can introduce flickering), 
                        'full' look for a middle ground. (Default: full)
  -l {quiet,fatal,error,warning,info,verbose,debug,trace}, --log {quiet,fatal,error,warning,info,verbose,debug,trace}
                        FFmpeg log mode, one of
                        (quiet|fatal|error|warning|info|verbose|debug|trace).
                        (Default: quiet)
  -e CHARENC, --encoding CHARENC
                        Subtitle encoding (it has effect only if a burning
                        option is enabled). (Default: UTF-8)
  -o, --onestep         Do not generate palette for the GIF. Tend to produce
                        worse, but way smaller GIFs. If used, --dither and
                        --bayer-scale parameters are ignored.
  -g, --gifsicle        Use gifsicle afterwards to validate, optimize and
                        compress it (require "gifsicle" executable reachable).
  --burn-sub-track BURN_TRACK
                        Burn in the GIF a source file subtitle track.
  --burn-sub-file BURN_FILE
                        Burn in the GIF an external subtitle file.
```

## Notes
- The default parameters for filters are often the best for a GIF
