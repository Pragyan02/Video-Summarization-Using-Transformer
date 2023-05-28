#!/usr/bin/env python
from __future__ import unicode_literals
import argparse
import os
import re
from itertools import starmap
import multiprocessing

import imageio
import youtube_dl
import chardet
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

from summarizer import Summarizer #bert extractive text summarizer

from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from datetime import datetime


imageio.plugins.ffmpeg.download()

def download_video_srt(subs):
    """ Downloads specified Youtube video's subtitles as a vtt/srt file.
    Args:
        subs(str): Full url of Youtube video
    Returns:
        True
    The video will be downloaded as 1.mp4 and its subtitles as 1.(lang).srt
    Both, the video and its subtitles, will be downloaded to the same location
    as that of this script (sum.py)
    """
    ydl_opts = {
        'format': 'best',
        'outtmpl': '1.%(ext)s',
        'subtitlesformat': 'srt',
        'writeautomaticsub': True,
        'writesubtitles': True
        # 'allsubtitles': True # Get all subtitles
    }

    movie_filename = ""
    subtitle_filename = ""
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # ydl.download([subs])
        result = ydl.extract_info("{}".format(subs), download=True)
        movie_filename = ydl.prepare_filename(result)
        subtitle_info = result.get("requested_subtitles")
        subtitle_language = list(subtitle_info.keys())[0]
        subtitle_ext = subtitle_info.get(subtitle_language).get("ext")
        subtitle_filename = movie_filename.replace(".mp4", ".%s.%s" %
                                                   (subtitle_language,
                                                    subtitle_ext))

    return movie_filename, subtitle_filename

def webvtt_to_txt(webvtt_file):
    """Extract text from WebVTT subtitles file

    Args:
        webvtt_file (str): The name of the WebVTT file

    Returns:
        str: Extracted text from subtitles file
    """
    text = ''
    with open(webvtt_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if "-->" in line:
            continue
        if line.strip() and not line.startswith(("Kind:", "Language:")):
            text += line.strip() + " "

    return text.strip().replace("WEBVTT", '')

def summarize_txt(filepath, ratio =0.3):
  text = webvtt_to_txt(filepath)
  model = Summarizer()
  result = model(text, min_length=60, max_length = 500 , ratio = ratio)
  summarized_text = ''.join(result)
  return summarized_text

def extract_timestamp_from_webvtt(file_path, sentence):
    timestamp = []
    with open(file_path, 'r') as file:
        contents = file.read()

    pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s-->\s(\d{2}:\d{2}:\d{2}\.\d{3})\n(.+?)\n\n'
    matches = re.findall(pattern, contents, re.DOTALL)
    
    for match in matches:
        start_time = match[0]
        end_time = match[1]
        text = match[2]
        text = re.sub(r'[\n\\]', '', text).replace(' ', '')
        # print(text)
        summarized_text = re.sub(r'[\n\\]', '', summarized_text).strip(r'"').replace(' ','')
        # print(summarized_text)
        if text in summarized_text:
            timestamp.append((start_time, end_time))

    return timestamp

def extract_summary_region(filepath, summarized_text):
  sentences = sent_tokenize(summarized_text)
  sent_to_dict = dict()
  for sentence in sentences:
    time = extract_timestamp_from_webvtt(filepath, sentence)
    # if len(time) == 1:
    sent_to_dict[sentence] = time 

  return sent_to_dict

def get_continuous_intervals(timestamp):
    continuous_intervals = []
    for i in range(len(timestamp) - 1):
        end_time = timestamp[i][1]
        start_time = timestamp[i+1][0]
        if end_time != start_time:
            continuous_intervals = timestamp[:i+1]
            return continuous_intervals    
        else:
          return timestamp

def final_clips(filepath, summarized_text):
  sent_to_dict = extract_summary_region(filepath, summarized_text)
  for sentence in sent_to_dict.keys():
    sent_to_dict[sentence] = get_continuous_intervals(sent_to_dict[sentence])
    start = sent_to_dict[sentence][0][0]
    end = sent_to_dict[sentence][-1][1]
    sent_to_dict[sentence] = [(start, end)]
  return sent_to_dict

def extract_seconds(timestamp):
    start_time = timestamp[0][0]
    end_time = timestamp[0][1]
    
    start_seconds = sum(x * float(t) for x, t in zip([3600, 60, 1], start_time.split(':')))
    end_seconds = sum(x * float(t) for x, t in zip([3600, 60, 1], end_time.split(':')))
    
    return start_seconds, end_seconds

# Iterate over the selected sentences and extract the corresponding video segments
def extract_summary_clips(video_path):
  video = VideoFileClip(video_path)
  clips = []
  for sentence, time_ in final_dict.items():

      start_time = time_[0][0]
      end_time = time_[0][1]
      
      start_seconds = sum(x * float(t) for x, t in zip([3600, 60, 1], start_time.split(':')))
      end_seconds = sum(x * float(t) for x, t in zip([3600, 60, 1], end_time.split(':')))
      
      clip = video.subclip(start_seconds, end_seconds)
      clips.append(clip)
  # Concatenate the video segments
  final_clip = concatenate_videoclips(clips)

  return final_clip

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Watch videos quickly")
    parser.add_argument('-u', '--url', help="Video url", type=str)
    parser.add_argument('-i', '--output-path', help="ouput video filepath")
    parser.add_argument('-k', '--keep-original-file',
                        help="Keep original movie & subtitle file",
                        action="store_true", default=False)

    args = parser.parse_args()

    url = args.url
    output_path = args.output_path
    keep_original_file = args.keep_original_file

    # download video with subtitles
    movie_filename, subtitle_filename = download_video_srt(url)
    summarized_text = summarize_txt(subtitle_filename, ratio = 0.3)
    final_clips = final_clips(subtitle_filename, summarized_text)
    summary_clips = extract_summary_clips(movie_filename)
    summary_clips.write_videofile(output_path, codec="libx264", audio_codec="aac")


    if not keep_original_file:
        os.remove(movie_filename)
        os.remove(subtitle_filename)
        print("[sum.py] Remove the original files")