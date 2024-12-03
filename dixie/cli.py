import os
import sys
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(file_dir)

import argparse
from scout import FileScout

def main():

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process a directory and query.")
    parser.add_argument('root_dir', type=str, help='The root directory to scout')
    parser.add_argument('query', type=str, help='The query for the scout')

    # Parse the arguments
    args = parser.parse_args()

    # Create the scout and start the observation
    scout = FileScout(args.root_dir, args.query)
    stop_event = scout.observe()
    scout.start()
    stop_event.set()

    # Print the summary
    print(scout.summary)

if __name__ == "__main__":
    main()
