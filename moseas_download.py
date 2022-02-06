import argparse
import pandas as pd
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Download youtube videos from a provided .csv file')
    parser.add_argument('file', type=str,
                        help='.csv file with video ids/links')
    parser.add_argument('col', type=str,
                        help='Name of column containing the ids/links')
    parser.add_argument('--dir', type=str, default="videos",
                        help='Directory to write videos to')
    parser.add_argument('--link', action="store_true",
                        help='Add if the file contains links and not video ids')
    parser.add_argument('--lines', type=int, default=-1,
                        help='Number of videos to download, default=all')
    parser.set_defaults(link=False)
    args = parser.parse_args()
    return args


def main():
    LINK_PREFIX = 'https://www.youtube.com/watch?v='

    args: argparse.Namespace = parse_args()

    table: pd.DataFrame
    try:
        table = pd.read_csv(args.file)
    except Exception:
        print("Could not read the file. Make sure it is a legal .csv file")
        sys.exit()

    links: pd.Series
    try:
        links = table[args.col]
    except KeyError:
        print("Provided column does not exist in the .csv file")
        sys.exit()

    if not args.link:
        links = links.map(lambda x: LINK_PREFIX + x)
    print(links)


if __name__ == '__main__':
    main()
