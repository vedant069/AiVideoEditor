from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from services.audio_enhance import AudioService
import scipy.io.wavfile as wav
from pathlib import Path

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
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/enhance-audio")
async def enhance_audio(file: UploadFile = File(...)):
    file_path = None
    enhanced_file_path = None
    
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
            
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the audio
        audio_service = AudioService()
        enhanced_file_path = await audio_service.process_audio(str(file_path))
        
        # Verify the enhanced file exists
        enhanced_path = Path(enhanced_file_path)
        if not enhanced_path.exists():
            raise HTTPException(status_code=500, detail="Failed to generate enhanced audio file")
            
        # Return the enhanced audio file
        return FileResponse(
            str(enhanced_path),
            media_type="audio/wav",
            filename=enhanced_path.name
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup uploaded files
        try:
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
        except Exception as cleanup_error:
            print(f"Error during cleanup: {str(cleanup_error)}")
        # Note: We don't delete the enhanced file here as it's being sent in the response