import os
from scipy.io import wavfile
import noisereduce as nr

class NoiseReducer:
    def __init__(self):
        self.uploads_dir = "uploads"
        os.makedirs(self.uploads_dir, exist_ok=True)

    async def reduce_noise(self, file_path: str) -> str:
        try:
            # Read the audio file
            rate, data = wavfile.read(file_path)
            
            # Perform noise reduction
            reduced_noise = nr.reduce_noise(y=data, sr=rate)
            
            # Generate output path
            output_path = os.path.join(self.uploads_dir, "reduced_noise.wav")
            
            # Save the noise-reduced audio
            wavfile.write(output_path, rate, reduced_noise)
            
            return output_path
        except Exception as e:
            print(f"Error reducing noise: {e}")
            raise e