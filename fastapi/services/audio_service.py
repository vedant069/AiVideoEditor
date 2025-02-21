import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from google import genai
import json
import re
import asyncio
import os
from pathlib import Path

class AudioService:
    def __init__(self):
        self.deepgram_api_key = 'a8b75fa07ad77e26a7866d995ed329553927767b'
        self.gemini_api_key = 'AIzaSyAOK9vRTSRQzd22B2gmbiuIePbZTDyaGYs'
        self.setup_clients()

    def setup_clients(self):
        """Initialize API clients"""
        self.deepgram = DeepgramClient(api_key=self.deepgram_api_key)
        self.genai = genai.Client(api_key=self.gemini_api_key)

    async def process_audio(self, file_path: str) -> str:
        """Process audio file and return path to enhanced version"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise Exception(f"Input file not found: {file_path}")
            
            enhanced_path = file_path.parent / f"{file_path.stem}_enhanced{file_path.suffix}"
            
            sample_rate, audio_data = wav.read(str(file_path))
            audio_data = audio_data.astype(np.float32)
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)  # Convert stereo to mono

            audio_data = audio_data / np.max(np.abs(audio_data))
            
            transcript = await self.transcribe_audio(str(file_path))
            if transcript is None:
                raise Exception("Transcription failed")
            
            parsed_output = self.parse_transcript(transcript)
            if parsed_output is None:
                raise Exception("Failed to parse transcript")
            
            optimized_output = await self.optimize_transcript(parsed_output)
            if optimized_output is None:
                raise Exception("Failed to optimize transcript")
            
            enhanced_audio = self.enhance_audio(audio_data, sample_rate, optimized_output)
            if enhanced_audio is None:
                raise Exception("Failed to enhance audio")
            
            enhanced_audio = np.int16(enhanced_audio * 32767)
            wav.write(str(enhanced_path), sample_rate, enhanced_audio)
            
            return str(enhanced_path)
            
        except Exception as e:
            print(f"Error in process_audio: {str(e)}")
            raise e

    async def transcribe_audio(self, filepath: str):
        """Transcribe audio file using Deepgram"""
        try:
            with open(filepath, 'rb') as file:
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
            print(f"Transcription error: {e}")
            return None

    def parse_transcript(self, response):
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

    async def optimize_transcript(self, transcription_json):
        """Optimize transcript using Gemini AI"""
        prompt = (
            "Optimize the following transcription JSON by removing duplicate phrases. "
            "If there are repeated segments, remove the duplicates and keep only the last occurrence, "
            "Make sure to not incluse any duplicates words and phrases"
            "preserving the start and end times of the retained words. "
            "Return the result in the exact JSON format as shown below:\n\n"
            "{\n"
            "  \"transcript\": str,\n"
            "  \"words\": [\n"
            "    {\n"
            "      \"word\": str,\n"
            "      \"timing\": {\n"
            "         \"start\": float,\n"
            "         \"end\": float\n"
            "      }\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            "Input: " + json.dumps(transcription_json)
        )

        response = self.genai.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        cleaned_text = re.sub(r'^```json\n|```$', '', response.text.strip())
        try:
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return transcription_json

    def enhance_audio(self, audio_data: np.ndarray, sample_rate: int, transcript_data: dict) -> np.ndarray:
        """Enhance the audio using the optimized transcript data to remove duplicates"""
        try:
            print("Starting audio enhancement...")
            print(f"Original audio shape: {audio_data.shape}, Sample rate: {sample_rate}")
            
            words = transcript_data.get("words", [])
            if not words:
                print("No word segments found in transcript data")
                return audio_data
            
            print(f"Processing {len(words)} word segments")
            enhanced_segments = []
            for i, word_info in enumerate(words):
                timing = word_info.get("timing", {})
                start_time = timing.get("start", 0)
                end_time = timing.get("end", 0)
                
                start_sample = int(start_time * sample_rate)
                end_sample = int(end_time * sample_rate)
                
                if start_sample >= end_sample or start_sample >= len(audio_data) or end_sample > len(audio_data):
                    print(f"Skipping invalid segment: {start_sample} to {end_sample}")
                    continue
                
                segment = audio_data[start_sample:end_sample].copy()
                enhanced_segments.append(segment)
            
            if not enhanced_segments:
                return audio_data
            
            enhanced = np.concatenate(enhanced_segments)
            enhanced = enhanced / np.max(np.abs(enhanced))
            return enhanced
            
        except Exception as e:
            print(f"Error in enhance_audio: {str(e)}")
            return audio_data
