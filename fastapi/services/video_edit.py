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
from moviepy.editor import VideoFileClip, concatenate_videoclips

def record_audio(duration=5, sample_rate=44100):
    """Record audio from the microphone."""
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate),
                        samplerate=sample_rate,
                        channels=1,
                        dtype=np.int16)
    sd.wait()
    print("Recording finished!")
    return audio_data, sample_rate

def save_audio(audio_data, sample_rate, filename):
    """Save audio data to a WAV file."""
    wav.write(filename, sample_rate, audio_data)
    return filename

def transcribe_audio(filepath):
    """Transcribe audio file using Deepgram."""
    try:
        # The Deepgram API key is hardcoded here.
        deepgram = DeepgramClient(api_key='a8b75fa07ad77e26a7866d995ed329553927767b')
        with open(filepath, 'rb') as file:
            buffer_data = file.read()
        payload: FileSource = {"buffer": buffer_data}
        options = PrerecordedOptions(
            model="nova-3",
            language='en',
            numerals=True,
        )
        print("Transcribing audio...")
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        return response
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

def parse_transcript(response):
    """Parse the Deepgram response to extract only the relevant information."""
    try:
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        words = response["results"]["channels"][0]["alternatives"][0]["words"]
        parsed_output = {
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
        return parsed_output
    except Exception as e:
        print(f"Error parsing transcript: {e}")
        return None

def display_transcript(transcript_json):
    """Display the transcript JSON in a formatted way."""
    if transcript_json:
        print(json.dumps(transcript_json, indent=2))

def optimize_transcript_with_gemini(transcription_json, gemini_api_key):
    """
    Optimize the transcription JSON by removing duplicate phrases.
    
    The prompt instructs Gemini to:
      - Remove any duplicate phrases.
      - If a phrase is repeated, keep only the last occurrence (with its timings).
      - Return the result in the same JSON schema:
      
        {
          "transcript": str,
          "words": [
            {
              "word": str,
              "timing": {
                 "start": float,
                 "end": float
              }
            },
            ...
          ]
        }
    """
    client = genai.Client(api_key=gemini_api_key)
    prompt = (
        "Optimize the following transcription JSON by removing duplicate phrases. "
        "If there are repeated segments, remove the duplicates and keep only the last occurrence, "
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

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    )
    # Remove any markdown formatting from the response.
    cleaned_text = re.sub(r'^```json\n|```$', '', response.text.strip())

    try:
        optimized_json = json.loads(cleaned_text)
        return optimized_json
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return transcription_json

def enhance_audio(original_audio, sample_rate, optimized_transcript):
    """
    Create an enhanced audio file by extracting and concatenating only the segments
    corresponding to the optimized transcript's words.
    """
    segments = []
    for word_info in optimized_transcript.get("words", []):
        timing = word_info.get("timing", {})
        start = timing.get("start", 0)
        end = timing.get("end", 0)
        start_idx = int(start * sample_rate)
        end_idx = int(end * sample_rate)
        # Append the segment corresponding to this word.
        segments.append(original_audio[start_idx:end_idx])
    
    if segments:
        # Concatenate all segments along the first axis.
        enhanced_audio = np.concatenate(segments, axis=0)
    else:
        enhanced_audio = original_audio
    return enhanced_audio

def extract_audio_from_video(video_path, audio_output="temp_audio.wav"):
    """
    Extract the audio track from a video file and save it as a WAV file.
    """
    try:
        print("Extracting audio from video...")
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_output, codec='pcm_s16le', fps=44100, verbose=False, logger=None)
        clip.close()
        return audio_output
    except Exception as e:
        print(f"Error extracting audio from video: {e}")
        return None

def enhance_video(video_path, optimized_transcript, output_video_file="enhanced_video.mp4"):
    """
    Create an enhanced video by extracting and concatenating only the segments
    corresponding to the optimized transcript's words.
    """
    try:
        print("Loading video for enhancement...")
        video = VideoFileClip(video_path)
        segments = []
        for word_info in optimized_transcript.get("words", []):
            timing = word_info.get("timing", {})
            start = timing.get("start", 0)
            end = timing.get("end", 0)
            # Ensure valid timings
            if start < end and end <= video.duration:
                segment = video.subclip(start, end)
                segments.append(segment)
        if segments:
            print("Concatenating video segments...")
            final_clip = concatenate_videoclips(segments)
            final_clip.write_videofile(output_video_file, codec="libx264", audio_codec="aac")
            final_clip.close()
        else:
            print("No valid segments found. Saving original video as enhanced video.")
            video.write_videofile(output_video_file, codec="libx264", audio_codec="aac")
        video.close()
        return output_video_file
    except Exception as e:
        print(f"Error enhancing video: {e}")
        return video_path

def process_video(video_path):
    """
    Process the video: extract audio, transcribe, optimize transcript,
    and enhance (trim) the video based on the optimized transcript.
    """
    # Step 1: Extract audio from video.
    temp_audio_file = extract_audio_from_video(video_path)
    if not temp_audio_file:
        print("Failed to extract audio from video.")
        return

    # Step 2: Transcribe the extracted audio.
    transcript = transcribe_audio(temp_audio_file)
    if transcript is None:
        print("Transcription failed.")
        return
    
    # Step 3: Parse and display the raw transcript.
    parsed_output = parse_transcript(transcript)
    print("Raw Transcript:")
    display_transcript(parsed_output)
    
    # Step 4: Optimize the transcript using Gemini.
    gemini_api_key = "AIzaSyAOK9vRTSRQzd22B2gmbiuIePbZTDyaGYs"  # Replace with your actual Gemini API key.
    optimized_output = optimize_transcript_with_gemini(parsed_output, gemini_api_key)
    print("\nOptimized Transcript:")
    display_transcript(optimized_output)
    
    # Step 5: Enhance the video by extracting segments from the optimized transcript.
    enhanced_video_file = enhance_video(video_path, optimized_output)
    print(f"\nEnhanced video saved to: {enhanced_video_file}")
    
    # Optionally, remove the temporary audio file.
    if os.path.exists(temp_audio_file):
        os.remove(temp_audio_file)

def main():
    try:
        choice = input("Would you like to process (audio) or (video)? Enter 'audio' or 'video': ").strip().lower()
        
        if choice == "audio":
            # Get recording duration from the user.
            duration = float(input("Enter recording duration in seconds: "))
            
            # Record audio.
            audio_data, sample_rate = record_audio(duration=duration)
            
            # Save the original raw audio.
            raw_audio_file = save_audio(audio_data, sample_rate, "recorded_audio.wav")
            print(f"Raw audio saved to: {raw_audio_file}")
            
            # Transcribe the raw audio.
            transcript = transcribe_audio(raw_audio_file)
            if transcript is None:
                print("Transcription failed.")
                return
            
            # Parse and display the raw transcript.
            parsed_output = parse_transcript(transcript)
            print("Raw Transcript:")
            display_transcript(parsed_output)
            
            # Optimize the transcript using the Gemini LLM.
            gemini_api_key = "AIzaSyAOK9vRTSRQzd22B2gmbiuIePbZTDyaGYs"  # Replace with your actual Gemini API key.
            optimized_output = optimize_transcript_with_gemini(parsed_output, gemini_api_key)
            print("\nOptimized Transcript:")
            display_transcript(optimized_output)
            
            # Enhance the audio by extracting segments from the optimized transcript.
            enhanced_audio = enhance_audio(audio_data, sample_rate, optimized_output)
            enhanced_audio_file = save_audio(enhanced_audio, sample_rate, "enhanced_audio.wav")
            print(f"\nEnhanced audio saved to: {enhanced_audio_file}")
        
        elif choice == "video":
            video_path = input("Enter the video file path: ").strip()
            if not Path(video_path).exists():
                print("Video file not found!")
                return
            process_video(video_path)
        
        else:
            print("Invalid choice. Please enter either 'audio' or 'video'.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
