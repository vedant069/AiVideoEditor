import os
import json
import re
import time
import traceback
import httpx
from yt_dlp import YoutubeDL
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from google import genai
from PIL import Image
try:
    Image.ANTIALIAS
except AttributeError:
    Image.ANTIALIAS = Image.Resampling.LANCZOS
import moviepy.config as mpy_config
mpy_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

from moviepy.editor import (VideoFileClip, concatenate_videoclips, 
                            ColorClip, CompositeVideoClip, TextClip)
from moviepy.video.tools.subtitles import SubtitlesClip

print("DEBUG: MoviePy imported successfully!")

#############################################
# Helper: Convert clip to mobile (vertical) view with letterboxing
#############################################
def convert_to_mobile(clip, target_width=720, target_height=1280, color=(0, 0, 0)):
    """
    Resize the input clip so that the entire video fits inside the target mobile resolution,
    then add padding (letterboxing) as necessary so that the final output has dimensions
    target_width x target_height. The default background color is black.
    """
    scale_factor = min(target_width / clip.w, target_height / clip.h)
    clip_resized = clip.resize(scale_factor)
    bg = ColorClip(size=(target_width, target_height), color=color, duration=clip.duration)
    composite = CompositeVideoClip([bg, clip_resized.set_position("center")])
    return composite

#############################################
# Helper: Overlay attractive dynamic subtitles using SubtitlesClip
#############################################
def overlay_subtitles(clip, subtitle_text, margin=50, fontsize=40, font="Arial-Bold", color="white"):
    """
    Split the full subtitle_text into chunks of 3-4 words and create a SubtitlesClip.
    The subtitles will be overlaid at the bottom center of the clip.
    """
    # Determine the duration of the clip
    duration = clip.duration
    # Split the text into words and group them into chunks (here, 4 words per chunk)
    words = subtitle_text.split()
    chunks = [' '.join(words[i:i+4]) for i in range(0, len(words), 4)]
    n = len(chunks)
    if n == 0:
        return clip
    chunk_duration = duration / n
    # Create a list of subtitle entries: (start_time, end_time, text)
    subtitle_entries = []
    for i, chunk in enumerate(chunks):
        start = i * chunk_duration
        end = (i + 1) * chunk_duration
        subtitle_entries.append((start, end, chunk))
    
    # Create the SubtitlesClip using a lambda function that returns a styled TextClip
    subtitles_clip = SubtitlesClip(subtitle_entries,
        lambda txt: TextClip(txt, fontsize=fontsize, font=font, color=color,
                               stroke_width=2, stroke_color="black", method="caption",
                               size=(clip.w - 2*margin, None))
    )
    # Position the subtitles near the bottom of the clip
    subtitles_clip = subtitles_clip.set_position(("center", clip.h - subtitles_clip.h - margin))
    
    composite = CompositeVideoClip([clip, subtitles_clip])
    return composite

#############################################
# 1. SIMPLE YOUTUBE VIDEO DOWNLOAD
#############################################
def simple_download_youtube_video(url, output_path="downloaded_video.mp4"):
    print("DEBUG: Starting download from URL:", url)
    ydl_opts = {'format': 'best', 'outtmpl': output_path}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"DEBUG: Downloaded video to {output_path}")
        return output_path
    except Exception as e:
        print("ERROR: Downloading video failed:", e)
        traceback.print_exc()
        return None

#############################################
# 2. SEGMENT VIDEO INTO 5-MINUTE CHUNKS
#############################################
def segment_video(video_file, segment_duration=300, output_dir="segments"):
    print("DEBUG: Starting segmentation of video:", video_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("DEBUG: Created output directory:", output_dir)
    segments = []
    try:
        with VideoFileClip(video_file) as clip:
            duration = clip.duration
            print(f"DEBUG: Video duration is {duration:.2f} seconds.")
            num_segments = int(duration // segment_duration) + (1 if duration % segment_duration > 0 else 0)
            print(f"DEBUG: Splitting video into {num_segments} segment(s).")
            for i in range(num_segments):
                start_time = i * segment_duration
                end_time = min((i + 1) * segment_duration, duration)
                segment_filename = os.path.join(output_dir, f"segment_{i:03d}.mp4")
                print(f"DEBUG: Creating segment {i+1}: start={start_time}s, end={end_time}s, saving as {segment_filename}")
                subclip = clip.subclip(start_time, end_time)
                subclip.write_videofile(segment_filename, codec='libx264', audio_codec='aac', verbose=False, logger=None)
                segments.append(segment_filename)
        print(f"DEBUG: Video segmented into {len(segments)} part(s).")
        return segments
    except Exception as e:
        print("ERROR: Segmenting video failed:", e)
        traceback.print_exc()
        return []

#############################################
# 3. AUDIO/VIDEO TRANSCRIPTION (Deepgram) WITH RETRY
#############################################
def transcribe_video_segment(filepath, deepgram_api_key, max_retries=3, delay=10):
    print(f"DEBUG: Starting transcription for segment: {filepath}")
    attempt = 0
    while attempt < max_retries:
        try:
            deepgram = DeepgramClient(api_key=deepgram_api_key)
            with open(filepath, 'rb') as file:
                buffer_data = file.read()
            payload: FileSource = {"buffer": buffer_data}
            options = PrerecordedOptions(model="nova-3", filler_words=True, utt_split=1,
                                         utterances=True, language='en', numerals=True, punctuate=True)
            response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
            print("DEBUG: Deepgram transcription complete for", filepath)
            return response
        except httpx.WriteTimeout:
            attempt += 1
            print(f"WARNING: Transcription attempt {attempt} for {filepath} timed out. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print("ERROR: Transcription failed for", filepath, ":", e)
            traceback.print_exc()
            return None
    print(f"ERROR: All {max_retries} attempts for transcription of {filepath} failed due to timeout.")
    return None

#############################################
# 4. REDUCE TRANSCRIPTION JSON TO ESSENTIAL FIELDS
#############################################
def reduce_transcription_json(transcription):
    print("DEBUG: Reducing transcription JSON.")
    if hasattr(transcription, 'to_dict'):
        transcription = transcription.to_dict()
    reduced = {"transcript": "", "words": []}
    try:
        alt = transcription["results"]["channels"][0]["alternatives"][0]
        reduced["transcript"] = alt.get("transcript", "")
        words = alt.get("words", [])
        reduced["words"] = [
            {"word": word["word"], "timing": {"start": round(word["start"], 2), "end": round(word["end"], 2)}}
            for word in words
        ]
        print("DEBUG: Reduced transcription contains", len(reduced["words"]), "words.")
    except Exception as e:
        print("ERROR: Reducing transcription failed:", e)
        traceback.print_exc()
    return reduced

#############################################
# 5. GENERATE SHORT VIDEO SCRIPTS WITH GEMINI-2.0-FLASH
#############################################
def generate_shorts_from_transcription(reduced_json, gemini_api_key, num_shorts=3):
    print("DEBUG: Generating short video scripts from transcription.")
    prompt = f"""You are an expert video content editor. You are given a JSON object representing the full transcription of a 5-minute video segment.
The JSON has two keys:
  "transcript": a string containing the full transcript,
  "words": a list of word objects, where each word object has:
      "word": the transcribed word,
      "timing": an object with "start" and "end" (in seconds).

Your task is to extract three coherent and engaging short video scripts from this transcription, each approximately 40 to 50 seconds long.
For each short video, remove duplicate or filler content so that the transcript is smooth and professional.
Determine the precise start and end times (using the word timings) that together cover about 40-50 seconds.
Return a JSON object with exactly three keys: "short1", "short2", and "short3". 
Each key's value must be an object with two keys:
  - "script": the edited short transcript,
  - "time_segments": a list of [start, end] pairs (in seconds) that together define the short clip.
Do not include any extra commentary. Use the input JSON exactly as provided.

Input JSON:
{json.dumps(reduced_json, indent=2)}
"""
    try:
        client = genai.Client(api_key=gemini_api_key)
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        cleaned_text = re.sub(r'^```json\n|```$', '', response.text.strip())
        result = json.loads(cleaned_text)
        print("DEBUG: Gemini response received:")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print("ERROR: Gemini short video generation failed:", e)
        traceback.print_exc()
        return None

#############################################
# 6. EXTRACT VIDEO CLIPS, CONVERT TO MOBILE VIEW, & OVERLAY DYNAMIC SUBTITLES
#############################################
def extract_video_clip(video_file, time_segments, output_file, subtitle_text=None):
    """
    Extract a video clip from the original video using the provided time segments,
    then convert the clip to a mobile-friendly (vertical) aspect ratio using letterboxing.
    If subtitle_text is provided, overlay dynamic subtitles that display 3-4 words at a time.
    Concatenates the segments using MoviePy.
    """
    print(f"DEBUG: Extracting video clip from {video_file} using segments: {time_segments}")
    try:
        clips = []
        with VideoFileClip(video_file) as clip:
            for seg in time_segments:
                start, end = seg
                subclip = clip.subclip(start, end)
                clips.append(subclip)
            final_clip = concatenate_videoclips(clips)
            final_clip = convert_to_mobile(final_clip, target_width=720, target_height=1280)
            # Overlay dynamic subtitles if provided
            if subtitle_text:
                duration = final_clip.duration
                words = subtitle_text.split()
                # Group words in chunks of 4 words
                chunks = [' '.join(words[i:i+4]) for i in range(0, len(words), 4)]
                n = len(chunks)
                chunk_duration = duration / n if n > 0 else duration
                subtitle_entries = []
                for i, chunk in enumerate(chunks):
                    start_time = i * chunk_duration
                    end_time = (i + 1) * chunk_duration
                    # Each entry is ((start, end), text)
                    subtitle_entries.append(((start_time, end_time), chunk))
                subtitles_clip = SubtitlesClip(subtitle_entries,
                    lambda txt: TextClip(txt, fontsize=40, font="Arial-Bold", color="white",
                                           stroke_width=2, stroke_color="black", method="caption",
                                           size=(final_clip.w - 100, None))
                )
                # Estimate text height using a temporary TextClip
                temp_text = TextClip("Test", fontsize=40, font="Arial-Bold", color="white",
                                     stroke_width=2, stroke_color="black", method="caption",
                                     size=(final_clip.w - 100, None))
                estimated_height = temp_text.h
                subtitles_clip = subtitles_clip.set_position(("center", final_clip.h - estimated_height - 50))
                final_clip = CompositeVideoClip([final_clip, subtitles_clip])
            final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        print(f"DEBUG: Extracted short clip saved to {output_file}")
        return output_file
    except Exception as e:
        print("ERROR: Extracting video clip failed:", e)
        traceback.print_exc()
        return None
#############################################
# 7. MAIN PIPELINE
#############################################
def main():
    try:
        deepgram_api_key = "a8b75fa07ad77e26a7866d995ed329553927767b"
        gemini_api_key = "AIzaSyAOK9vRTSRQzd22B2gmbiuIePbZTDyaGYs"
        
        yt_url = input("Enter YouTube video URL: ")
        print("DEBUG: Received URL:", yt_url)
        video_file = simple_download_youtube_video(yt_url)
        if video_file is None:
            print("ERROR: Video download failed. Exiting.")
            return
        
        segments = segment_video(video_file, segment_duration=300)
        if not segments:
            print("ERROR: No video segments produced. Exiting.")
            return
        
        for seg in segments:
            print(f"\nDEBUG: Processing segment: {seg}")
            transcription_response = transcribe_video_segment(seg, deepgram_api_key)
            if transcription_response is None:
                print("WARNING: Transcription failed for segment. Skipping this segment.")
                continue
            reduced_json = reduce_transcription_json(transcription_response)
            short_videos_data = generate_shorts_from_transcription(reduced_json, gemini_api_key, num_shorts=3)
            if short_videos_data is None:
                print("WARNING: Gemini short video generation failed. Skipping this segment.")
                continue
            
            for key in ["short1", "short2", "short3"]:
                short = short_videos_data.get(key)
                if not short:
                    print(f"WARNING: No data returned for {key}.")
                    continue
                script = short.get("script", "")
                time_segs = short.get("time_segments", [])
                print(f"\nDEBUG: {key} generated:")
                print("Script:")
                print(script)
                print("Time Segments (s):")
                print(time_segs)
                output_clip = f"{key}_{os.path.basename(seg)}"
                extract_video_clip(seg, time_segs, output_clip, subtitle_text=script)
                
    except Exception as e:
        print("ERROR: Exception in main pipeline:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
