import { useState, useRef } from 'react';
import { Video } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { createHighlights } from '@/services/api';

export function VideoHighlighter() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [originalVideo, setOriginalVideo] = useState<string | null>(null);
  const [highlightVideo, setHighlightVideo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setError(null);
      setIsProcessing(true);
      
      // Create URL for original video
      const originalUrl = URL.createObjectURL(file);
      setOriginalVideo(originalUrl);
      
      // Process and create highlights
      const highlightUrl = await createHighlights(file);
      setHighlightVideo(highlightUrl);
    } catch (err) {
      setError('Failed to create highlights. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDownload = () => {
    if (highlightVideo) {
      const link = document.createElement('a');
      link.href = highlightVideo;
      link.download = 'highlights.mp4';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center gap-3 mb-4">
        <Video className="w-6 h-6 text-gray-900" />
        <h2 className="text-lg font-semibold text-gray-900">Video Highlights</h2>
      </div>
      
      <div className="space-y-4">
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        <Button 
          onClick={handleUploadClick}
          variant="outline" 
          className="w-full"
          disabled={isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Upload Video'}
        </Button>

        {isProcessing && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Creating highlights...</p>
          </div>
        )}

        {error && (
          <div className="text-red-500 text-sm text-center">{error}</div>
        )}

        {originalVideo && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-900">Original Video</h3>
            <video controls className="w-full rounded-lg">
              <source src={originalVideo} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {highlightVideo && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-900">Highlights</h3>
            <video controls className="w-full rounded-lg">
              <source src={highlightVideo} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            <Button 
              onClick={handleDownload} 
              className="w-full"
              disabled={isProcessing}
            >
              Download Highlights
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
