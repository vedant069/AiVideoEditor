import os
import json
import re
from pathlib import Path
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from google import genai
from moviepy.editor import VideoFileClip, concatenate_videoclips
from typing import Optional, Dict, List

class VideoEditService:
    def __init__(self):
        self.deepgram_api_key = 'a8b75fa07ad77e26a7866d995ed329553927767b'
        self.gemini_api_key = 'AIzaSyAOK9vRTSRQzd22B2gmbiuIePbZTDyaGYs'
        self.uploads_dir = "uploads"
        os.makedirs(self.uploads_dir, exist_ok=True)
        self.setup_clients()

    def setup_clients(self):
        """Initialize API clients"""
        self.deepgram = DeepgramClient(api_key=self.deepgram_api_key)

    def transcribe_audio(self, filepath: str) -> Optional[Dict]:
        """Transcribe audio file using Deepgram."""
        try:
            with open(filepath, 'rb') as audio:
                buffer_data = audio.read()
            
            payload: FileSource = {"buffer": buffer_data}
            options = PrerecordedOptions(
                model="nova-3",
                language='en',
                numerals=True,
            )
            
            response = self.deepgram.listen.rest.v("1").transcribe_file(payload, options)
            return response
        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def parse_transcript(self, transcript: Dict) -> Dict:
        """Parse the transcript response into a structured format."""
        try:
            words = transcript["results"]["channels"][0]["alternatives"][0]["words"]
            transcript_text = transcript["results"]["channels"][0]["alternatives"][0]["transcript"]
            
            return {
                "transcript": transcript_text,
                "words": [
                    {
                        "word": word["word"],
                        "timing": {
                            "start": round(word["start"], 2),
                            "end": round(word["end"], 2)
                        }
                    }
                    for word in words
                ]
            }
        except Exception as e:
            print(f"Error parsing transcript: {e}")
            return {"transcript": "", "words": []}

    def optimize_transcript_with_gemini(self, transcript_data: Dict) -> Dict:
        """Use Gemini to optimize and clean the transcript."""
        try:
            client = genai.Client(api_key=self.gemini_api_key)
            
            prompt = (
                "You are a video editing expert. Given this transcript data, identify the key segments "
                "that should be kept in the final video. Focus on complete thoughts and important content. "
                "Return the result in the same format as the input, keeping only the selected segments.\n\n"
                f"Input transcript data: {json.dumps(transcript_data)}\n\n"
                "Return the optimized transcript in the exact same JSON format with 'transcript' and 'words' fields."
            )
            
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            # Clean and parse the response
            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text.split('```')[1]
                if cleaned_text.startswith('json'):
                    cleaned_text = cleaned_text[4:].strip()
            
            optimized_data = json.loads(cleaned_text)
            return optimized_data
        except Exception as e:
            print(f"Error optimizing transcript: {e}")
            return transcript_data

    def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """Extract audio from video file."""
        try:
            audio_path = os.path.join(self.uploads_dir, "temp_audio.wav")
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            return audio_path
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    def create_edited_video(self, video_path: str, transcript_data: Dict) -> Optional[str]:
        """Create edited video from transcript segments."""
        video = None
        final_video = None
        try:
            video = VideoFileClip(video_path)
            clips = []
            
            # Sort words by start time
            words = sorted(transcript_data["words"], key=lambda x: x["timing"]["start"])
            
            # Group consecutive words into segments
            segments = []
            current_segment = {"start": words[0]["timing"]["start"], "end": words[0]["timing"]["end"]}
            
            for i in range(1, len(words)):
                current_word = words[i]
                if current_word["timing"]["start"] - current_segment["end"] > 0.5:  # Gap threshold
                    segments.append(current_segment)
                    current_segment = {"start": current_word["timing"]["start"], "end": current_word["timing"]["end"]}
                else:
                    current_segment["end"] = current_word["timing"]["end"]
            segments.append(current_segment)
            
            # Create video clips from segments
            for segment in segments:
                if segment["start"] < segment["end"] and segment["end"] <= video.duration:
                    clip = video.subclip(segment["start"], segment["end"])
                    clips.append(clip)

            if not clips:
                return None

            output_path = os.path.join(self.uploads_dir, "edited_video.mp4")
            final_video = concatenate_videoclips(clips)
            final_video.write_videofile(output_path, verbose=False, logger=None)
            return output_path

        except Exception as e:
            print(f"Error creating edited video: {e}")
            return None
        finally:
            if video is not None:
                video.close()
            if final_video is not None:
                final_video.close()

    async def process_video(self, video_path: str) -> Optional[str]:
        """Process video and create an edited version."""
        audio_path = None
        try:
            # Extract audio
            audio_path = self.extract_audio_from_video(video_path)
            if not audio_path:
                raise Exception("Failed to extract audio")

            # Transcribe audio
            transcript = self.transcribe_audio(audio_path)
            if not transcript:
                raise Exception("Failed to transcribe audio")

            # Parse transcript
            parsed_transcript = self.parse_transcript(transcript)
            if not parsed_transcript["words"]:
                raise Exception("Failed to parse transcript")

            # Optimize transcript
            optimized_transcript = self.optimize_transcript_with_gemini(parsed_transcript)
            if not optimized_transcript["words"]:
                raise Exception("Failed to optimize transcript")

            # Create edited video
            output_path = self.create_edited_video(video_path, optimized_transcript)
            if not output_path:
                raise Exception("Failed to create edited video")

            return output_path

        except Exception as e:
            print(f"Error in process_video: {str(e)}")
            raise e
        finally:
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as e:
                    print(f"Error cleaning up audio file: {e}")
