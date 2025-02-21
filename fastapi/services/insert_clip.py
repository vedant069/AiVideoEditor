import subprocess
import os

def get_video_duration(video_path):
    """
    Get the duration (in seconds) of a video using ffprobe.
    """
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        output = subprocess.check_output(cmd).strip()
        return float(output)
    except Exception as e:
        print(f"Error getting duration of {video_path}: {e}")
        return 0

def insert_stock_video(base_video, stock_video, insertion_time, output_file):
    """
    Insert a stock video into the base video at a given insertion_time.
    
    The stock video will be overlaid on the base video during the insertion period.
    The base video's audio remains unchanged.
    
    Parameters:
      base_video: Path to the base video file.
      stock_video: Path to the stock video file (or uploaded by the user).
      insertion_time: The time (in seconds) in the base video where the stock video should start.
      output_file: Path to the final output video file.
    """
    # Get the stock video duration.
    stock_duration = get_video_duration(stock_video)
    if stock_duration <= 0:
        print("Stock video duration invalid.")
        return None

    # Build the FFmpeg command.
    # The overlay filter is enabled between the insertion_time and insertion_time+stock_duration.
    # We assume that the stock video will be scaled to match the base video's dimensions.
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", base_video,
        "-i", stock_video,
        "-filter_complex",
        f"[1:v]setpts=PTS-STARTPTS,scale=iw:ih[stock];[0:v][stock]overlay=enable='between(t,{insertion_time},{insertion_time + stock_duration})'[v]",
        "-map", "[v]",
        "-map", "0:a",
        "-c:a", "copy",
        output_file
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Stock video inserted. Output saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error inserting stock video: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    base_video = "base_video.mp4"   # Path to your base video.
    stock_video = "stock_clip.mp4"  # Path to the stock video to insert.
    insertion_time = 60             # Insert stock video at 60 seconds.
    output_file = "output_with_stock.mp4"
    
    insert_stock_video(base_video, stock_video, insertion_time, output_file)
