from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from services.audio_service import AudioService
from services.video_service import VideoService
from services.noise_reduce import NoiseReducer
from services.highlight import HighlightService
from services.video_edit import VideoEditService
import scipy.io.wavfile as wav
import shutil

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/shorts", exist_ok=True)

# Mount the shorts directory
app.mount("/shorts", StaticFiles(directory="uploads/shorts"), name="shorts")

# Initialize services
video_edit_service = VideoEditService()

@app.post("/enhance-audio")
async def enhance_audio(file: UploadFile = File(...)):
    file_path = None
    enhanced_file_path = None
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
            
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the audio
        audio_service = AudioService()
        enhanced_file_path = await audio_service.process_audio(file_path)
        
        # Return the enhanced audio file
        response = FileResponse(
            enhanced_file_path,
            media_type="audio/wav",
            filename="enhanced_audio.wav"
        )
        
        # Clean up the input file immediately
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        return response
    except Exception as e:
        # Clean up any files if there's an error
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if enhanced_file_path and os.path.exists(enhanced_file_path):
            os.remove(enhanced_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reduce-noise")
async def reduce_noise(file: UploadFile = File(...)):
    file_path = None
    reduced_noise_path = None
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a WAV file.")
            
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the audio
        noise_reducer = NoiseReducer()
        reduced_noise_path = await noise_reducer.reduce_noise(file_path)
        
        # Return the noise-reduced audio file
        response = FileResponse(
            reduced_noise_path,
            media_type="audio/wav",
            filename="reduced_noise.wav"
        )
        
        # Clean up the input file immediately
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        return response
    except Exception as e:
        # Clean up any files if there's an error
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if reduced_noise_path and os.path.exists(reduced_noise_path):
            os.remove(reduced_noise_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-highlights")
async def create_highlights(file: UploadFile = File(...)):
    file_path = None
    highlight_path = None
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")
            
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the video
        highlight_service = HighlightService()
        highlight_path = await highlight_service.create_highlights(file_path)
        
        # Return the highlight video file
        response = FileResponse(
            highlight_path,
            media_type="video/mp4",
            filename="highlights.mp4",
            background=None  # This ensures the file is sent before cleanup
        )
        
        # Let the response be sent before cleaning up
        return response
    except Exception as e:
        # Clean up any files if there's an error
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if highlight_path and os.path.exists(highlight_path):
                os.remove(highlight_path)
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/edit-video")
async def edit_video(file: UploadFile = File(...)):
    """Edit a video by removing unnecessary segments using AI."""
    try:
        # Save uploaded file
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the video
        output_path = await video_edit_service.process_video(file_path)
        
        if not output_path or not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to process video")

        # Return the processed video
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="edited_video.mp4"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/process-youtube")
async def process_youtube(url: str = Form(...)):
    try:
        video_service = VideoService()
        shorts = await video_service.process_youtube_video(url)
        
        if not shorts:
            raise HTTPException(status_code=500, detail="Failed to process video")
        
        # Return the paths to the generated shorts
        return {
            "shorts": [
                {
                    "url": f"/shorts/{os.path.basename(short['file'])}",
                    "script": short['script']
                }
                for short in shorts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))