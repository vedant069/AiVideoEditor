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

class VideoService:
    def __init__(self):
        self.deepgram_api_key = 'a8b75fa07ad77e26a7866d995ed329553927767b'
        self.gemini_api_key = 'AIzaSyAi6inimWToyS6KWMwPrU02gwKn_u5_Ca0'
        self.output_dir = "uploads/shorts"
        os.makedirs(self.output_dir, exist_ok=True)

    async def process_youtube_video(self, url: str) -> list:
        try:
            # Download video
            video_file = await self.download_youtube_video(url)
            if not video_file:
                raise Exception("Failed to download video")

            # Process video segments
            segments = await self.segment_video(video_file)
            if not segments:
                raise Exception("Failed to segment video")

            shorts = []
            for segment in segments:
                # Process each segment
                segment_shorts = await self.process_segment(segment)
                shorts.extend(segment_shorts)

            return shorts

        except Exception as e:
            print(f"Error processing YouTube video: {e}")
            traceback.print_exc()
            raise

    async def download_youtube_video(self, url: str) -> str:
        output_path = os.path.join(self.output_dir, "downloaded_video.mp4")
        ydl_opts = {'format': 'best', 'outtmpl': output_path}
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return output_path
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None

    async def segment_video(self, video_file: str, segment_duration: int = 300) -> list:
        segments = []
        segments_dir = os.path.join(self.output_dir, "segments")
        os.makedirs(segments_dir, exist_ok=True)

        try:
            with VideoFileClip(video_file) as clip:
                duration = clip.duration
                num_segments = int(duration // segment_duration) + (1 if duration % segment_duration > 0 else 0)
                
                for i in range(num_segments):
                    start_time = i * segment_duration
                    end_time = min((i + 1) * segment_duration, duration)
                    segment_filename = os.path.join(segments_dir, f"segment_{i:03d}.mp4")
                    
                    subclip = clip.subclip(start_time, end_time)
                    subclip.write_videofile(segment_filename, codec='libx264', audio_codec='aac')
                    segments.append(segment_filename)

            return segments
        except Exception as e:
            print(f"Error segmenting video: {e}")
            return []

    async def process_segment(self, segment_file: str) -> list:
        try:
            # Transcribe segment
            transcription = await self.transcribe_video(segment_file)
            if not transcription:
                return []

            # Generate shorts data
            shorts_data = await self.generate_shorts(transcription)
            if not shorts_data:
                return []

            # Create short videos
            shorts = []
            for idx, (key, short) in enumerate(shorts_data.items()):
                output_file = os.path.join(self.output_dir, f"short_{idx}_{os.path.basename(segment_file)}")
                short_video = await self.create_short_video(
                    segment_file,
                    short["time_segments"],
                    output_file,
                    short["script"]
                )
                if short_video:
                    shorts.append({
                        "file": short_video,
                        "script": short["script"]
                    })

            return shorts

        except Exception as e:
            print(f"Error processing segment: {e}")
            return []

    async def transcribe_video(self, filepath: str):
        try:
            deepgram = DeepgramClient(api_key=self.deepgram_api_key)
            with open(filepath, 'rb') as file:
                buffer_data = file.read()
            
            payload = {"buffer": buffer_data}
            options = PrerecordedOptions(
                model="nova-3",
                language='en',
                numerals=True
            )
            
            response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
            return self.reduce_transcription(response)
        except Exception as e:
            print(f"Error transcribing video: {e}")
            return None

    def reduce_transcription(self, transcription):
        if hasattr(transcription, 'to_dict'):
            transcription = transcription.to_dict()
        
        reduced = {"transcript": "", "words": []}
        try:
            alt = transcription["results"]["channels"][0]["alternatives"][0]
            reduced["transcript"] = alt.get("transcript", "")
            reduced["words"] = [
                {
                    "word": word["word"],
                    "timing": {
                        "start": round(word["start"], 2),
                        "end": round(word["end"], 2)
                    }
                }
                for word in alt.get("words", [])
            ]
        except Exception as e:
            print(f"Error reducing transcription: {e}")
        
        return reduced

    async def generate_shorts(self, transcription):
        try:
            client = genai.Client(api_key=self.gemini_api_key)
            prompt = self.create_shorts_prompt(transcription)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            cleaned_text = re.sub(r'^```json\n|```$', '', response.text.strip())
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"Error generating shorts: {e}")
            return None

    def create_shorts_prompt(self, transcription):
        return f"""You are an expert video content editor. You are given a JSON object representing the full transcription of a 5-minute video segment.
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
{json.dumps(transcription)}
"""

    async def create_short_video(self, video_file, time_segments, output_file, subtitle_text):
        try:
            clips = []
            with VideoFileClip(video_file) as clip:
                for start, end in time_segments:
                    subclip = clip.subclip(start, end)
                    clips.append(subclip)
                
                final_clip = concatenate_videoclips(clips)
                final_clip = self.convert_to_mobile(final_clip)
                
                if subtitle_text:
                    final_clip = self.add_subtitles(final_clip, subtitle_text)
                
                final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
                return output_file
        except Exception as e:
            print(f"Error creating short video: {e}")
            return None

    def convert_to_mobile(self, clip, target_width=720, target_height=1280):
        scale_factor = min(target_width / clip.w, target_height / clip.h)
        clip_resized = clip.resize(scale_factor)
        bg = ColorClip(size=(target_width, target_height), color=(0, 0, 0), duration=clip.duration)
        return CompositeVideoClip([bg, clip_resized.set_position("center")])

    def add_subtitles(self, clip, text, fontsize=40):
        words = text.split()
        chunks = [' '.join(words[i:i+4]) for i in range(0, len(words), 4)]
        duration = clip.duration
        chunk_duration = duration / len(chunks) if chunks else duration
        
        subtitle_entries = [
            ((i * chunk_duration, (i + 1) * chunk_duration), chunk)
            for i, chunk in enumerate(chunks)
        ]
        
        subtitles = SubtitlesClip(subtitle_entries,
            lambda txt: TextClip(
                txt,
                fontsize=fontsize,
                font="Arial-Bold",
                color="white",
                stroke_width=2,
                stroke_color="black",
                method="caption",
                size=(clip.w - 100, None)
            )
        )
        
        subtitles = subtitles.set_position(("center", clip.h - 150))
        return CompositeVideoClip([clip, subtitles])