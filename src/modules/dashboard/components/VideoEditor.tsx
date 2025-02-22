import React, { useState } from 'react';
import { editVideo } from '../../../services/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

const VideoEditor: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [editedVideoUrl, setEditedVideoUrl] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setEditedVideoUrl(null);
    }
  };

  const handleEditVideo = async () => {
    if (!selectedFile) return;

    try {
      setIsProcessing(true);
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await editVideo(formData);
      const blob = new Blob([response.data], { type: 'video/mp4' });
      const url = URL.createObjectURL(blob);
      setEditedVideoUrl(url);
    } catch (error) {
      console.error('Error editing video:', error);
      alert('Failed to edit video. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col space-y-2">
        <Button
          variant="outline"
          className="w-full"
          disabled={isProcessing}
          onClick={() => document.getElementById('video-upload')?.click()}
        >
          Upload Video
          <input
            id="video-upload"
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </Button>

        {selectedFile && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium mb-2">Original Video:</h3>
              <video
                controls
                className="w-full max-h-[300px] rounded-lg"
                src={previewUrl || undefined}
              />
              <Button
                className="mt-2 w-full"
                onClick={handleEditVideo}
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Edit Video'
                )}
              </Button>
            </div>
          </div>
        )}

        {editedVideoUrl && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium mb-2">Edited Video:</h3>
              <video
                controls
                className="w-full max-h-[300px] rounded-lg"
                src={editedVideoUrl}
              />
              <Button
                variant="outline"
                className="mt-2 w-full"
                asChild
              >
                <a href={editedVideoUrl} download="edited_video.mp4">
                  Download Edited Video
                </a>
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoEditor;
