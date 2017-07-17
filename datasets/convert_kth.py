import os
import sys
import argparse
from multiprocessing import Pool


def do_command(command):
    print command
    os.system(command)


def starto(args):
    image_size = args.imageSize
    data_root = args.dataRoot
    force_delete = args.forceDelete
    frame_rate = 25

    if not os.path.isdir(data_root):
        print 'Error with data directory: {}'.format(data_root)

    classes = ['boxing', 'handclapping', 'handwaving', 'jogging', 'running', 'walking']


    raw_dir = os.path.join(data_root, 'raw')
    processed_dir = os.path.join(data_root, 'processed')

    ffmpeg_command_strings = []

    for c in classes:
        print ' ---- '
        class_path = os.path.join(raw_dir, c)

        print 'Looking in {}'.format(class_path)
        if not os.path.isdir(class_path):
            print 'Class path not found! Skipping...'
            continue

        for vid in os.listdir(class_path):
            vid_path = os.path.join(class_path, vid)
            print 'Found video: {}'.format(vid_path)
            fname = vid[:-11]
            doing_frames_dir = os.path.join(processed_dir, c, fname)
            print 'Make directory: {}'.format(doing_frames_dir)
            conditional_delete_dir(force_delete, doing_frames_dir)

            os.makedirs(doing_frames_dir) # mkdir on single thread
            ffmpeg_command_strings.append('ffmpeg -i {} -r {} -f image2 -s {}x{}  {}/image-%03d_{}x{}.png'
                                          .format(vid_path, frame_rate, image_size, image_size, doing_frames_dir, image_size, image_size))

    threadPool = Pool()
    threadPool.map(do_command, ffmpeg_command_strings)
    threadPool.close()
    threadPool.join()


def conditional_delete_dir(force_delete, processed_dir):
    if os.path.isdir(processed_dir):
        if force_delete:
            print 'Deleting existing {}.'.format(processed_dir)
            os.rmdir(processed_dir)
            return

        getting = raw_input('Directory found! Delete? (y/[N]) >')
        if str(getting).lower() == 'y':
            print 'Deleting existing {}.'.format(processed_dir)
            os.rmdir(processed_dir)
        else:
            print 'Bye.'
            sys.exit(0)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--imageSize', dest='imageSize', default=128, type=int, help='The image size for processed pictures')
    ap.add_argument('-d', dest='dataRoot', type=str, help='The root folder of desired data.')
    ap.add_argument('--f', dest='forceDelete', type=int, help='Delete frames directories if found', default=0)

    if not len(sys.argv) > 1:
        ap.print_help()
        sys.exit(0)

    args = ap.parse_args()
    starto(args)