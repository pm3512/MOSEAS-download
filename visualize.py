import argparse
from typing import List
import pandas as pd
import cv2 as cv
from enum import Enum

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Download youtube videos from a provided .csv file')
    parser.add_argument('video_path', type=str,
                        help='Path to video for visualization')
    parser.add_argument('features_path', type=str,
                        help='Path to .csv file with containing features')
    args = parser.parse_args()
    return args

def draw_point(frame, x: float, y: float):
    return cv.circle(frame, (int(x),int(y)), radius=3, color=(0, 0, 255), thickness=-1)

def main():
    args: argparse.Namespace = parse_args()

    features: pd.DataFrame = pd.read_csv(args.features_path)
    xs = features.filter(regex=("^x_.*"))
    ys = features.filter(regex=("^y_.*"))
    num_points = len(xs.columns)
    print(xs.columns)

    cap = cv.VideoCapture(args.video_path)
    while True:
        ret, frame = cap.read()
        frame_num = int(cap.get(cv.CAP_PROP_POS_FRAMES))
        for point in range(num_points):
            print()
            frame = draw_point(frame, xs[f'x_{str(point)}'][frame_num], ys[f'y_{str(point)}'][frame_num])
        cv.imshow('window name', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
            cap.release()
            cv.destroyAllWindows()

if __name__ == '__main__':
    main()
