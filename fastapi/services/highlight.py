import os
import asyncio
from moviepy.editor import VideoFileClip, concatenate_videoclips
from google import genai
import json
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from typing import Optional, Dict, List, Any

class HighlightService:
    def __init__(self):
        self.deepgram_api_key = 'a8b75fa07ad77e26a7866d995ed329553927767b'
        self.gemini_api_key = 'AIzaSyAOK9vRTSRQzd22B2gmbiuIePbZTDyaGYs'
        self.setup_clients()
        self.uploads_dir = "uploads"
        os.makedirs(self.uploads_dir, exist_ok=True)

    def setup_clients(self):
        """Initialize API clients"""
        self.deepgram = DeepgramClient(api_key=self.deepgram_api_key)

    async def extract_audio(self, video_path: str) -> Optional[str]:
        """Extract audio from video file"""
        try:
            video = VideoFileClip(video_path)
            audio_path = os.path.join(self.uploads_dir, "temp_audio.wav")
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            return audio_path
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    async def transcribe_with_retry(self, audio_path: str, max_retries: int = 3) -> Optional[Dict]:
        """Transcribe audio with retry logic"""
        for attempt in range(max_retries):
            try:
                with open(audio_path, 'rb') as file:
                    buffer_data = file.read()
                
                payload: FileSource = {"buffer": buffer_data}
                options = PrerecordedOptions(
                    model="nova-3",
                    language='en',
                    numerals=True,
                )
                
                response = self.deepgram.listen.rest.v("1").transcribe_file(payload, options)
                return response
            except Exception as e:
                print(f"Transcription attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("Waiting 10 seconds before retrying...")
                    await asyncio.sleep(10)
                else:
                    print("All transcription attempts failed")
                    return None

    def parse_transcript(self, response: Dict) -> Optional[Dict]:
        """Parse the Deepgram response"""
        try:
            transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
            words = response["results"]["channels"][0]["alternatives"][0]["words"]
            return {
                "transcript": transcript,
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
            return None

    async def get_highlight_segments(self, transcript_data: Dict) -> Optional[List[Dict[str, float]]]:
        """Get highlight segments using Gemini"""
        try:
            prompt = (
                "You are a video highlight expert. Analyze this video transcript and identify 3-5 most interesting "
                "segments that would make good highlights. Each highlight should be 10-30 seconds long. "
                "Return the result as a JSON array of objects with 'start' and 'end' timestamps in seconds.\n\n"
                "Transcript data:\n" + json.dumps(transcript_data) + "\n\n"
                "Return format example:\n"
                "[{'start': 10.5, 'end': 35.2}, {'start': 120.0, 'end': 145.3}]"
            )

            client = genai.Client(api_key=self.gemini_api_key)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text.split('```')[1]
                if cleaned_text.startswith('json'):
                    cleaned_text = cleaned_text[4:].strip()
            
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"Error getting highlights: {e}")
            return None

    async def create_highlight_video(self, video_path: str, highlights: List[Dict[str, float]]) -> Optional[str]:
        """Create highlight video from segments"""
        video = None
        final_video = None
        try:
            video = VideoFileClip(video_path)
            clips = []
            for highlight in highlights:
                start = highlight['start']
                end = highlight['end']
                if start < end and end <= video.duration:
                    clip = video.subclip(start, end)
                    clips.append(clip)

            if not clips:
                print("No valid highlight segments found")
                return None

            output_path = os.path.join(self.uploads_dir, "highlights.mp4")
            final_video = concatenate_videoclips(clips)
            final_video.write_videofile(output_path, verbose=False, logger=None)
            return output_path

        except Exception as e:
            print(f"Error creating highlight video: {e}")
            return None
        finally:
            if video is not None:
                video.close()
            if final_video is not None:
                final_video.close()

    async def create_highlights(self, video_path: str) -> str:
        """Create highlights from a video file"""
        audio_path = None
        try:
            # Step 1: Extract audio from video
            audio_path = await self.extract_audio(video_path)
            if not audio_path:
                raise Exception("Failed to extract audio from video")

            # Step 2: Transcribe audio with retry logic
            transcript = await self.transcribe_with_retry(audio_path)
            if not transcript:
                raise Exception("Transcription failed after all retries")

            # Step 3: Parse transcript
            parsed_transcript = self.parse_transcript(transcript)
            if not parsed_transcript:
                raise Exception("Failed to parse transcript")

            # Step 4: Get highlight segments using Gemini
            highlights = await self.get_highlight_segments(parsed_transcript)
            if not highlights:
                raise Exception("No highlights found")

            # Step 5: Create highlight video
            output_path = await self.create_highlight_video(video_path, highlights)
            if not output_path:
                raise Exception("Failed to create highlight video")

            return output_path

        except Exception as e:
            print(f"Error in create_highlights: {str(e)}")
            raise e
        finally:
            # Clean up temporary audio file
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as e:
                    print(f"Error cleaning up audio file: {e}")
