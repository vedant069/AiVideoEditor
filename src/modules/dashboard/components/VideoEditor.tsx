import React, { useState } from 'react';
import { editVideo } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Loader2, Upload } from 'lucide-react';

interface VideoEditorProps {
  selectedVideo: File | null;
  onVideoSelect: (file: File) => void;
}

export function VideoEditor({ selectedVideo, onVideoSelect }: VideoEditorProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [editedVideoUrl, setEditedVideoUrl] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onVideoSelect(file);
      setPreviewUrl(URL.createObjectURL(file));
      setEditedVideoUrl(null);
    }
  };

  const handleProcessVideo = async () => {
    if (!selectedVideo) return;

    try {
      setIsProcessing(true);
      const editedUrl = await editVideo(selectedVideo);
      setEditedVideoUrl(editedUrl);
    } catch (error) {
      console.error('Error processing video:', error);
      alert('Failed to process video. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-4">
      <input
        type="file"
        accept="video/*"
        onChange={handleFileSelect}
        className="hidden"
        id="video-upload"
      />
      
      <label htmlFor="video-upload">
        <Button
          variant="outline"
          className="w-full border-white/20 text-white hover:bg-white/10"
          disabled={isProcessing}
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload Video
        </Button>
      </label>

      {selectedVideo && previewUrl && (
        <div className="p-4 bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700">
          <h3 className="text-sm font-medium text-white mb-2">Original Video</h3>
          <video controls className="w-full rounded-lg bg-black/20 mb-4">
            <source src={previewUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          
          <Button
            onClick={handleProcessVideo}
            className="w-full bg-purple-500 hover:bg-purple-600 text-white"
            disabled={isProcessing}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              'Process Video'
            )}
          </Button>
        </div>
      )}

      {editedVideoUrl && (
        <div className="p-4 bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700">
          <h3 className="text-sm font-medium text-white mb-2">Edited Video</h3>
          <video controls className="w-full rounded-lg bg-black/20">
            <source src={editedVideoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          
          <Button
            onClick={() => {
              const link = document.createElement('a');
              link.href = editedVideoUrl;
              link.download = 'edited-video.mp4';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }}
            className="w-full mt-4 bg-green-500 hover:bg-green-600 text-white"
          >
            Download Edited Video
          </Button>
        </div>
      )}
    </div>
  );
}
