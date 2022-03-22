import argparse
import os
import sys
import re
from typing import List
from tqdm import tqdm
import shutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Create directory according to MOSEAS specs')
    parser.add_argument('source', type=str,
                        help='Directory with .mp4 videos')
    parser.add_argument('dest', type=str,
                        help='Output destination')
    parser.add_argument('--overwrite', action="store_true",
                        help='Add to overwrite existing files')
    parser.add_argument('--extractor', type=str, default="bin/FeatureExtraction",
                        help='Path to the FeatureExtraction binary')
    parser.set_defaults(overwrite=False)
    args = parser.parse_args()
    return args


def make_dirs(args: argparse.Namespace):

    def try_mkdir(path: str, overwrite: bool):
        if os.path.isdir(path) and overwrite:
            shutil.rmtree(path)
        if not os.path.isdir(path):
            os.mkdir(path)

    try_mkdir(args.dest, args.overwrite)

    if not os.path.isdir(args.source):
        print("Source directory does not exist")
        sys.exit()

    source_files: List[str] = os.listdir(args.source)
    for file in source_files:
        if not re.match('^[a-zA-Z0-9_-]{11}\.[mM][pP]4$', file):
            print("File {} is not a valid YouTube video id .mp4 file".format(file))
            sys.exit()

    TOTAL_OPS = len(source_files) * 5

    with tqdm(total=TOTAL_OPS, miniters=1) as pbar:
        for file in source_files:
            id: str = file[:-4]
            pbar.write('Processing video with id {}'.format(id))
            dir_path: str = os.path.join(args.dest, id)
            source_path: str = os.path.join(args.source, file)
            try_mkdir(dir_path, args.overwrite)
            for subdir in ['video', 'audio', 'feature_extraction']:
                try_mkdir(os.path.join(dir_path, subdir), args.overwrite)

            if args.overwrite or not os.path.isfile(os.path.join(dir_path, 'video', file)):
                shutil.copy(source_path,
                            os.path.join(dir_path, 'video', file))
            pbar.update(1)

            if args.overwrite or not os.path.isfile(os.path.join(dir_path, 'video', id + '_30fps.mp4')):
                os.system('ffmpeg -y -i {} -filter:v fps=30 {} -hide_banner -loglevel error'
                          .format(source_path,
                                  os.path.join(dir_path, 'video', id + '_30fps.mp4')))
            pbar.update(1)

            if args.overwrite or not os.path.isfile(os.path.join(dir_path, 'audio', id + '.wav')):
                os.system('ffmpeg -y -i {} -vn -acodec pcm_s16le -ar 44100 -ac 2 {} -hide_banner -loglevel error'
                          .format(source_path,
                                  os.path.join(dir_path, 'audio', id + '.wav')))
            pbar.update(1)

            if args.overwrite or not os.path.isfile(os.path.join(dir_path, 'audio', id + '_16hz.wav')):
                os.system('ffmpeg -i {} -ar 16000 {} -hide_banner -loglevel error'
                          .format(os.path.join(dir_path, 'audio', id + '.wav'),
                                  os.path.join(dir_path, 'audio', id + '_16hz.wav')))
            pbar.update(1)

            if args.overwrite or not os.path.isdir(os.path.join(dir_path, 'feature_extraction', 'openface')):
                os.system('{} -f {} {} -out_dir {}'
                          .format(args.extractor, os.path.join(dir_path, 'video', id + '_30fps.mp4'),
                                  '-q -2Dfp -3Dfp -pose -aus -gaze -multi-view 1 -wild',
                                  os.path.join(dir_path, 'feature_extraction', 'openface')))
            pbar.update(1)
        pbar.close()


def main():
    args: argparse.Namespace = parse_args()
    make_dirs(args)


if __name__ == '__main__':
    main()
