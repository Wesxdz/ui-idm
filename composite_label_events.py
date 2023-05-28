import argparse
import glob
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading
import time

# Custom TTF font
custom_font = "ATARISTOCRAT.ttf"

def create_text_clip(idx, row, next_row):
    # Log the progress
    print(f"Thread {threading.current_thread().name} - Creating text clip for event {idx+1}/{total_events}")
    time.sleep(0.1)  # to ensure print statements don't overlap

    # Create a TextClip for the sentence
    text_clip = TextClip(row['event'], fontsize=24, color='white', font=custom_font)

    # Set the start time for the text clip
    start_time = row['time_diff']

    # Get the time difference of the next row for end time
    end_time = next_row['time_diff'] if not next_row.empty else start_time + 1.0

    text_clip = text_clip.set_start(start_time).set_end(end_time)

    # Set the position of the text clip (centered)
    text_clip = text_clip.set_position((96, 8))

    return text_clip

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process video file and log.')
parser.add_argument('directory', type=str, help='path to the directory containing the video and text file')
args = parser.parse_args()

# Get the path to the video and text file
video_files = glob.glob(os.path.join(args.directory, '*.mkv'))
text_file = glob.glob(os.path.join(args.directory, '*.txt'))[0]

# Check if a video file exists
if len(video_files) == 0:
    print("No video file found in the specified directory.")
    exit(1)
elif len(video_files) > 1:
    print("Multiple video files found in the specified directory. Please provide only one video file.")
    exit(1)

# Load the input video
clip = VideoFileClip(video_files[0])

# Parse the log file
log = pd.read_csv(text_file, header=None, names=['timestamp', 'event'], sep=' - ')
log['timestamp'] = pd.to_datetime(log['timestamp'])

# Compute time difference in seconds from the start of the video
start_time = log['timestamp'].iloc[0]
log['time_diff'] = (log['timestamp'] - start_time).dt.total_seconds()

# Total number of events
total_events = len(log)

# List to hold all clips (including the base video)
clips = [clip]

# Prepare data for multithreading
data = [(idx, row, log.shift(-1).loc[idx]) for idx, row in log.iterrows()]

# Create a ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=16) as executor:
    # Use map to apply create_text_clip to each tuple in data and collect the results
    text_clips = list(executor.map(lambda params: create_text_clip(*params), data))

    # Add text_clips to the list of clips
    clips.extend(text_clips)

# Create a composite video clip with all text clips and the original video
final_clip = CompositeVideoClip(clips)

# Write the output video file
output_file = os.path.join(args.directory, 'output.mp4')
final_clip.write_videofile(output_file)

print(f"Video file saved as {output_file}")
