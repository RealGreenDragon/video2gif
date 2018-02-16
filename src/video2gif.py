
"""
MIT License

Copyright (c) 2018 Daniele Giudice

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function
from subprocess import call
from datetime import datetime
import sys, traceback, time, os, re, argparse, shlex, logging

__title__           = 'video2gif'
__version__         = '0.1'
__author__          = 'Daniele Giudice'
__license__         = 'MIT License'
__copyright__       = 'Copyright 2018 Daniele Giudice'
__description__     = 'FFmpeg wrapper to easily create GIFs from videos (also with subtitles)'

''' Logging '''

# NullHandler was added in python v2.7
if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None

LOGGER = logging.getLogger(__title__)
LOG_FORMAT = logging.Formatter('[%(asctime)s] %(levelname)8s - %(name)s: %(message)s')

''' Constants '''

IS_WIN = sys.platform.startswith('win32') | sys.platform.startswith('cygwin')

TIMESTAMP = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H-%M-%S')

CURRENT_DIR = os.path.dirname( os.path.abspath(__file__) )
PALETTE_MKV = os.path.join(CURRENT_DIR, TIMESTAMP+'_palette.mkv')
PALETTE_PNG = os.path.join(CURRENT_DIR, TIMESTAMP+'_palette.png')
SUB_EXTRACTED = os.path.join(CURRENT_DIR, TIMESTAMP+'_subtitle.ass')

RESIZE_FILTERS = ['lanczos', 'bicubic', 'spline16', 'spline36', 'point', 'bilinear']
DITHER_MODES = ['bayer', 'floyd_steinberg', 'sierra2', 'sierra2_4a', 'none']
BAYER_SCALES = [0, 1, 2, 3, 4, 5]
GENERATION_MODES = ['full', 'diff', 'single']
LOG_MODES = ['quiet', 'fatal', 'error', 'warning', 'info', 'verbose', 'debug', 'trace']
LOG_DEBUG = LOG_MODES[4:]

SUBS_FILTER  = 'subtitles={subtitles}:charenc={charenc},'
BASE_FILTERS = 'fps={fps},scale={size}:flags={resize_mode}'
PALETTEUSE   = 'paletteuse=diff_mode={diff_mode}:dither={dither}:bayer_scale={bayer_scale}:new={new}'
COMMANDS = {
    'subextract'        : 'ffmpeg -v {log} -y -sub_charenc "{charenc}" {cutting} -i "{sourceVideo}" -map 0:s:{burn_track} "{subtitles_unescaped}"', 
    'subcut'            : 'ffmpeg -v {log} -y -sub_charenc "{charenc}" {cutting} -i "{burn_file}" "{subtitles_unescaped}"', 
    'palettegen'        : 'ffmpeg -v {log} -y {cutting} -i "{sourceVideo}" -vf "{sub_filters}{filters},palettegen=stats_mode={mode}" "{palette}"', 
    'gifcreate'         : 'ffmpeg -v {log} -y {cutting} -i "{sourceVideo}" -i "{palette}" -lavfi "{sub_filters}{filters}[x];[x][1:v]{paletteuse}" -f gif "{destinationGif}"', 
    'gifcreate_onestep' : 'ffmpeg -v {log} -y {cutting} -i "{sourceVideo}" -vf "{sub_filters}{filters}" -f gif "{destinationGif}"', 
    'gifsicle'          : 'gifsicle -b -O3 "{destinationGif}" -o "{destinationGifOpt}"', 
}

''' Utils '''

def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '%02d:%02d:%02d' % (h, m, s)

def ffmpeg_escape(s):
    if IS_WIN:
        # Seems that in Windows ffmpeg requires a special escape for filter options
        # https://trac.ffmpeg.org/ticket/3334#comment:7
        # return s.replace('\\', '\\\\\\\\\\\\\\\\\\').replace(':', '\\\\\\:')
        return re.escape(s).replace('\\\\', '\\\\\\\\\\\\\\\\\\').replace('\\:', '\\\\\\:')
    else:
        return re.escape(s)

def clean_files(args):
    print('An error occurred!')
    
    # Remove temp and dirty files
    if os.path.isfile(args['subtitles_unescaped']):
        os.remove(args['subtitles_unescaped'])
    if os.path.isfile(args['palette']):
        os.remove(args['palette'])
    if os.path.isfile(args['destinationGif']):
        os.remove(args['destinationGif'])
    if os.path.isfile(args['destinationGifOpt']):
        os.remove(args['destinationGifOpt'])

def check_programs(args):
    global FNULL
    
    programs = ['ffmpeg']
    if args['optimize']:
        programs.append('gifsicle')
    
    missing = []
    for p in programs:
        try:
            call(p, stdout=FNULL, stderr=FNULL)
        except OSError:
            missing.append(p)
    
    return missing

def cmd_exec(cmd_name, args):
    global FNULL
    
    # Exec command line
    cmd_line = COMMANDS[cmd_name].format(**args)
    if args['log'] in LOG_DEBUG:
        LOGGER.debug('Exec command line:\n%s\n\n' % cmd_line)
        res = call(shlex.split(cmd_line), stdout=sys.stderr)
        print('\n', file=sys.stderr)
    else:
        res = call(shlex.split(cmd_line), stdout=FNULL, stderr=FNULL)
    
    # In case of errors, clean and exit
    if res != 0:
        clean_files(args)
        raise SystemExit
    

''' Args parser '''

def int_not_negative(value):
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError("'%s' is a negative int value" % value)
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError("'%s' is not an int value" % value)

def file_path_read(fpath):
    try:
        if not (os.path.isfile(fpath) and os.access(fpath, os.R_OK)):
            raise argparse.ArgumentTypeError("'%s' is not a valid path or the file is not readable" % fpath)
        return fpath
    except OSError:
        raise argparse.ArgumentTypeError("'%s' is not a valid path or the file is not readable" % fpath)

def file_path_write(fpath):
    try:
        if not os.access(os.path.abspath(os.path.join(fpath, os.pardir)), os.W_OK):
            raise argparse.ArgumentTypeError("'%s' is not a valid path or the directory is not writable" % fpath)
        return fpath
    except OSError:
        raise argparse.ArgumentTypeError("'%s' is not a valid path or the directory is not writable" % fpath)

def size_string(size_str):
    '''
    Check if the size string passed is correct and purge it
    
    A size string is invalid if:
    - is None or empty
    - contains more or less than one ':'
    - contains non digit chars
    - not respect the pattern WIDTH:HEIGHT
    - WIDTH or HEIGHT are positive integers (but both can be 0, that means 'keep the rateo'
    
    Args:
        size_str (str): The raw time string

    Returns:
        str: the size string purged
    
    Raises:
        argparse.ArgumentTypeError: if the size string passed is invalid
    '''
    
    try:
        # Strip the size string
        size_str = size_str.strip()
        
        # Base checks
        if not size_str:
            raise argparse.ArgumentTypeError("'%s' is not a valid size" % size_str)
        
        # Check pattern
        size_split = size_str.split(':')
        if not size_str or len(size_split)!=2:
            raise argparse.ArgumentTypeError("'%s' is not a valid size" % size_str)
        
        width, height = int(size_split[0]), int(size_split[1])
        if width<0 or height<0:
            raise argparse.ArgumentTypeError("'%s' is not a valid size" % size_str)
        
        # If one value is 0, convert to -1 (FFmpeg standard to keep rateo)
        if width == 0:  width  = -1
        if height == 0: height = -1
        
        # Rebuild the size string
        return '{}:{}'.format(width, height)
    except (ValueError, IndexError) as ex:
        raise argparse.ArgumentTypeError("'%s' is not a valid size" % size_str)

def time_string_to_secs(time_string):
    '''
    Check if the time string passed is correct and convert it to seconds
    
    A time string is invalid if:
    - is None or empty
    - contains ',' (to separate seconds and microseconds is used '.')
    - ends with '.'
    - contains non digit chars
    - not respect the pattern ((HH:)MM:)SS(.mm)
    
    Args:
        time_string (str): The raw time string

    Returns:
        float: the time string converted into seconds
    
    Raises:
        argparse.ArgumentTypeError: if the time string passed is invalid
    '''
    
    try:
        # Strip the time string
        time_string = time_string.strip()
        
        # Base checks
        if not time_string or ',' in time_string or time_string.endswith('.'):
            raise argparse.ArgumentTypeError("'%s' is not a valid time" % time_string)
        
        # Check pattern (to preserve the leading zeros in microseconds, keep seconds field value as a string)
        t_split = time_string.split(':')
        if not t_split or len(t_split) > 3:
            raise argparse.ArgumentTypeError("'%s' is not a valid time" % time_string)
        elif len(t_split) == 3:
            # 'hours' and 'mins'
            hours = int(t_split[0])
            mins = int(t_split[1])
            secs_str = t_split[2]
        elif len(t_split) == 2:
            # no 'hours' and 'mins'
            hours = 0
            mins = int(t_split[0])
            secs_str = t_split[1]
        else:
            # no 'hours' and no 'mins'
            hours = 0
            mins = 0
            secs_str = t_split[0]
        
        # Parse seconds and microseconds (to preserve the leading zeros, keep microseconds as a string)
        s_split = secs_str.split('.')
        if not s_split or len(s_split) > 2:
            raise argparse.ArgumentTypeError("'%s' is not a valid time" % time_string)
        elif len(t_split) == 2:
            # 'seconds' and 'microseconds'
            seconds  = int(s_split[0])
            mseconds_str = s_split[1]
        else:
            # 'seconds' and no 'microseconds'
            seconds  = int(s_split[0])
            mseconds_str = '0'
        
        # Final conversions
        seconds = hours * 3600 + mins * 60 + seconds
        return float('{}.{}'.format(seconds, mseconds_str))
    except (ValueError, IndexError) as ex:
        raise argparse.ArgumentTypeError("'%s' is not a valid time" % time_string)

def get_args():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        'sourceVideo',
        type=file_path_read,
        help='Source video path'
    )
    parser.add_argument(
        'destinationGif',
        type=file_path_write,
        help='Output GIF path'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='Version: %s - Author: %s' % (__version__, __author__)
    )
    parser.add_argument(
        '-f',
        '--fps',
        default=15,
        dest='fps',
        type=int_not_negative,
        help='Set the fps. (Default: 15)'
    )
    parser.add_argument(
        '-s',
        '--size',
        default='640:0',
        dest='size',
        type=size_string,
        help='GIF size, in WIDTH:HEIGHT format. "0" can be used to keep the ratio ("0:0" keep video size). (Default: 640:0)'
    )
    parser.add_argument(
        '-r', 
        '--resize-mode',
        default=RESIZE_FILTERS[0],
        dest='resize_mode',
        choices=RESIZE_FILTERS,
        help='Resize filter, one of (%s). (Default: %s)' % ('|'.join(RESIZE_FILTERS), RESIZE_FILTERS[0])
    )
    parser.add_argument(
        '-a',
        '--at',
        default=-1,
        dest='start',
        type=time_string_to_secs,
        help='Moment in which the GIF begins, in seconds or "HH:MM:SS[.m+]" time format. If setted, must be lower than --to param. (Default: 0)'
    )
    parser.add_argument(
        '-t', 
        '--to',
        default=-1,
        dest='end',
        type=time_string_to_secs,
        help='Moment in which the GIF ends, in seconds or "HH:MM:SS[.m+]" time format. If setted, must be greater than --at param. (Default: Till end)'
    )
    parser.add_argument(
        '-d',
        '--dither',
        default=DITHER_MODES[0],
        dest='dither',
        choices=DITHER_MODES,
        help='Dithering algorithm to use. One of (%s). (Default: %s)' % ('|'.join(DITHER_MODES), DITHER_MODES[0])
    )
    parser.add_argument(
        '-b',
        '--bayer-scale',
        default=2,
        dest='bayer_scale',
        choices=BAYER_SCALES,
        help='Select the Bayer algorithm scale factor, in the range [0 - 5] (used only if --dither is "bayer"). Lower values tend to produce less artefacts but larger images. (Default: 2)'
    )
    parser.add_argument(
        '-m',
        '--mode',
        default='full',
        dest='mode',
        choices=GENERATION_MODES,
        help="Color generation mode, one of (full|diff|single). 'diff' optimize the colors of moving objects at the cost of the background quality, 'single' optimize the colors for each frame (but can introduce flickering), 'full' look for a middle ground. (Default: full)"
    )
    parser.add_argument(
        '-l',
        '--log',
        default=LOG_MODES[0],
        dest='log',
        choices=LOG_MODES,
        help='FFmpeg log mode, one of (%s). (Default: %s)' % ('|'.join(LOG_MODES), LOG_MODES[0])
    )
    parser.add_argument(
        '-e',
        '--encoding',
        default='UTF-8',
        dest='charenc',
        help='Subtitle encoding (it has effect only if a burning option is enabled). (Default: UTF-8)'
    )
    parser.add_argument(
        '-o',
        '--onestep',
        dest='onestep',
        action='store_true',
        help='Do not generate palette for the GIF. Tend to produce worse, but way smaller GIFs. If used --mode, --dither and --bayer-scale parameters are ignored.'
    )
    parser.add_argument(
        '-g',
        '--gifsicle',
        dest='optimize',
        action='store_true',
        help='Use gifsicle afterwards to validate, optimize and compress it (require "gifsicle" executable reachable).'
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--burn-sub-track',
        default=-1,
        dest='burn_track',
        type=int_not_negative,
        help='Burn in the GIF a source file subtitle track.'
    )
    group.add_argument(
        '--burn-sub-file',
        default=None,
        dest='burn_file',
        type=file_path_read,
        help='Burn in the GIF an external subtitle file.'
    )
    
    # Parse args
    args = vars(parser.parse_args())
    
    # Check if cutting points are valid
    if args['start'] >= 0 and args['end'] >= 0 and args['start'] == args['end']:
        parser.error('Start cutting point is greater or equal than end cutting point')
    
    # Init logger
    if args['log'] in LOG_DEBUG:
        _log_handler = logging.StreamHandler()
        _log_handler.setFormatter(LOG_FORMAT)
        _log_level = logging.DEBUG
    else:
        _log_handler = NullHandler()
        _log_level = logging.WARN
    LOGGER.setLevel(_log_level)
    LOGGER.addHandler(_log_handler)
    LOGGER.debug('%s debug module init finished', __title__)
    
    # Check if there are all programs (and update them)
    missing_programs = check_programs(args)
    if missing_programs:
        print('Missing programs: %s' % ', '.join(missing_programs))
        return
    
    return args

''' Main '''

def vid2gif():
    print('Video To GIF v%s\n' % __version__)
    
    # If the OS is windows, set env vars for font config
    if IS_WIN:
        os.environ['FC_CONFIG_DIR']     = os.path.join(CURRENT_DIR, 'fonts')
        os.environ['FONTCONFIG_PATH']   = os.path.join(CURRENT_DIR, 'fonts')
        os.environ['FONTCONFIG_FILE']   = 'fonts.conf'
    
    # Get start time
    start_time = time.time()
    
    # Parse and check args
    args = get_args()
    
    # Format start cutting point cmd option
    ss = ''
    if args['start'] >= 0:
        ss = '-ss %f' % args['start']
    
    # Format end cutting point cmd option
    t = ''
    if args['end'] >= 0:
        if args['start'] >= 0:
            # If start cutting point is valid and greater than zero, convert end cutting point to gif duration (in seconds)
            t = '-t %f' % (args['end'] - args['start'])
        else:
            t = '-t %f' % args['end']
    
    args['cutting'] = (ss + ' ' + t).strip()
    
    # Fix some params and insert util params
    single_mode = args['mode']=='single'
    args['diff_mode'] = 'rectangle' # This is the best 'diff_mode' offered, so is always set
    args['palette'] = PALETTE_MKV if single_mode else PALETTE_PNG
    args['new'] = 1 if single_mode else 0 # Take new palette for each output frame
    args['subtitles_unescaped'] = SUB_EXTRACTED
    args['subtitles'] = ffmpeg_escape(SUB_EXTRACTED)
    args['charenc'] = ''.join(args['charenc'].upper().split()) # All uppercase and remove spaces
    args['destinationGifOpt'] = ''
    args['sub_filters'] = ''
    
    # Filters (fps and resize)
    args['filters'] = BASE_FILTERS.format(**args)
    
    # Paletteuse
    args['paletteuse'] = PALETTEUSE.format(**args)
    
    # Edit 'destinationGif' and 'destinationGifOpt' if 'optimize' is enabled
    if args['optimize']:
        args['destinationGif'], args['destinationGifOpt'] = ('not_opt_'+args['destinationGif'], args['destinationGif'])
    
    # Check if a subtitle option is enabled
    sub_command = ''
    if args['burn_track'] > -1:
        sub_command = 'subextract' 
    elif args['burn_file']:
        sub_command = 'subcut'
    
    # GIF creation
    try:
        # Prepare subtitles (if an option is enabled)
        if sub_command:
            print('Extracting subtitles...')
            cmd_exec(sub_command, args)
            
            # Create subtitle filter string
            args['sub_filters'] = SUBS_FILTER.format(**args)
        
        if args['onestep']:
            # Create GIF without palette
            print('Creating GIF...')
            cmd_exec('gifcreate_onestep', args)
        else:
            # Create GIF with palette
            print('Creating Palette...')
            cmd_exec('palettegen', args)
            
            print('Creating GIF...')
            cmd_exec('gifcreate', args)
            
            # Delete palette file
            if os.path.isfile(args['palette']):
                os.remove(args['palette'])
        
        # Delete extracted subtitles
        if os.path.isfile(args['subtitles_unescaped']):
            os.remove(args['subtitles_unescaped'])
        
        # GIF optimization
        if args['optimize']:
            print('Optimize GIF...')
            cmd_exec('gifsicle', args)
            
            # Remove old GIF
            if os.path.isfile(args['destinationGif']):
                os.remove(args['destinationGif'])
        
    except (OSError, IOError) as e:
        clean_files(args)
        traceback.print_exc(file=sys.stdout)
    
    # Print time enlapsed
    time_elapsed = format_time( time.time() - start_time )
    print('\nFinished - Time elapsed -> %s' % time_elapsed)


if __name__ == "__main__":
    global FNULL

    FNULL = open(os.devnull, 'w')
    try:
        vid2gif()
        FNULL.close()
    except:
        FNULL.close()
