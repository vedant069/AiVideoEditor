import { useState, useRef } from 'react';
import { Video } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { createHighlights } from '@/services/api';
import { toast } from 'sonner';

interface VideoHighlighterProps {
  selectedVideo: File | null;
  onVideoSelect: (file: File) => void;
}

export function VideoHighlighter({ selectedVideo, onVideoSelect }: VideoHighlighterProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [originalVideo, setOriginalVideo] = useState<string | null>(null);
  const [highlightVideo, setHighlightVideo] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('video/')) {
      toast.error('Please upload a valid video file');
      return;
    }

    // Validate file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
      toast.error('Video file size should be less than 100MB');
      return;
    }

    onVideoSelect(file);

    try {
      setIsProcessing(true);
      
      // Create URL for original video
      const originalUrl = URL.createObjectURL(file);
      setOriginalVideo(originalUrl);
      
      // Process and create highlights
      const highlightUrl = await createHighlights(file);
      setHighlightVideo(highlightUrl);
      toast.success('Highlights created successfully!');
    } catch (err) {
      toast.error('Failed to create highlights. Please try again.');
      console.error('Highlight creation error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDownload = () => {
    if (highlightVideo) {
      try {
        const link = document.createElement('a');
        link.href = highlightVideo;
        link.download = 'highlights.mp4';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        toast.success('Download started!');
      } catch (err) {
        toast.error('Failed to download highlights');
        console.error('Download error:', err);
      }
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-white/20">
      <div className="flex items-center gap-3 mb-4">
        <Video className="w-6 h-6 text-purple-400" />
        <h2 className="text-lg font-semibold text-white">Video Highlights</h2>
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
          className="w-full border-white/20 text-white hover:bg-white/10"
          disabled={isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Upload Video'}
        </Button>

        {isProcessing && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-300">Creating highlights...</p>
          </div>
        )}

        {originalVideo && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-white">Original Video</h3>
            <video controls className="w-full rounded-lg bg-black/20">
              <source src={originalVideo} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {highlightVideo && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-white">Highlights</h3>
            <video controls className="w-full rounded-lg bg-black/20">
              <source src={highlightVideo} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            <Button 
              onClick={handleDownload} 
              className="w-full bg-purple-500 hover:bg-purple-600 text-white"
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
