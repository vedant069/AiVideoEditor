import { useState } from 'react';
import { Play, Pause } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ShortVideoProps {
  videoUrl: string;
  script: string;
}

export function ShortVideo({ videoUrl, script }: ShortVideoProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState(false);

  const togglePlay = (videoElement: HTMLVideoElement) => {
    if (isPlaying) {
      videoElement.pause();
    } else {
      videoElement.play().catch(() => {
        setError(true);
      });
    }
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <div className="relative aspect-[9/16] bg-black">
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center text-white text-center p-4">
            <p>Error loading video. Please try refreshing the page.</p>
          </div>
        ) : (
          <>
            <video
              src={`http://localhost:8000${videoUrl}`}
              className="w-full h-full object-contain"
              onEnded={() => setIsPlaying(false)}
              onClick={(e) => togglePlay(e.currentTarget)}
            />
            <Button
              onClick={(e) => {
                e.stopPropagation();
                const video = e.currentTarget.parentElement?.querySelector('video');
                if (video) togglePlay(video);
              }}
              variant="primary"
              size="lg"
              className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 rounded-full p-0 flex items-center justify-center bg-black/50 hover:bg-black/70"
            >
              {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8" />}
            </Button>
          </>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-medium text-gray-900 mb-2">Generated Short</h3>
        <p className="text-sm text-gray-600">{script}</p>
      </div>
    </div>
  );
}