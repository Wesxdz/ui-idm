# postprocess.py
import sys
import os
import shutil
import time
import ffmpeg

LOGFILE = "log.txt"
print("postprocess")

# # Load your video
storage = "sessions/"
video_path = sys.argv[1]
video_name = video_path.split('/')[-1].split('.')[0]
tmp_path = './' + storage + video_name

# Create destination directory if it doesn't exist
os.makedirs(tmp_path, exist_ok=True)

def convert_mkv_to_mp4(input_file, output_file):
    ffmpeg.input(input_file).output(output_file, vcodec='copy', acodec='copy').run()

# Example usage
time.sleep(3)
shutil.move(video_path, tmp_path)
shutil.move(LOGFILE, storage + video_name + '/' + video_name + ".txt")

# Postprocessing to composite event labels is computationally expensive,
# so it is disable by default...

# input_file = tmp_path
# output_file = video_path.split('/')[-1].split('.')[0] + '.mp4'
# convert_mkv_to_mp4(input_file, output_file)

# from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
# from datetime import datetime
# import pandas as pd

# # Load the input video
# clip = VideoFileClip(output_file)

# # Parse the log file
# log = pd.read_csv('log.txt', header=None, names=['timestamp', 'event'], sep=' - ')
# log['timestamp'] = pd.to_datetime(log['timestamp'])

# # Compute time difference in seconds from the start of the video
# start_time = log['timestamp'].iloc[0]
# log['time_diff'] = (log['timestamp'] - start_time).dt.total_seconds()

# # Custom TTF font
# custom_font = "ATARISTOCRAT.ttf"

# # List to hold all clips (including the base video)
# clips = [clip]

# for idx, row in log.iterrows():
#     # Create a TextClip for the sentence
#     text_clip = TextClip(row['event'], fontsize=24, color='white', font=custom_font)

#     # Set the start time for the text clip
#     start_time = row['time_diff']

#     # Get the time difference of the next row for end time
#     next_row = log.shift(-1).loc[idx]
#     end_time = next_row['time_diff'] if not next_row.empty else start_time + 1.0

#     text_clip = text_clip.set_start(start_time).set_end(end_time)

#     # Set the position of the text clip (centered)
#     text_clip = text_clip.set_position((8, 8))

#     # Add to the list of clips
#     clips.append(text_clip)

# # Create a composite video clip with all text clips and the original video
# final_clip = CompositeVideoClip(clips)

# # Write the output video file
# final_clip.write_videofile(video_path.split('/')[-1].split('.')[0] + '_events' + '.mp4')
