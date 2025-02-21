import { useState } from 'react';
import { Video } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProcessingStatus } from './ProcessingStatus';

interface YoutubeProcessorProps {
  onShortsGenerated: (shorts: Array<{ url: string; script: string }>) => void;
}

export function YoutubeProcessor({ onShortsGenerated }: YoutubeProcessorProps) {
  const [url, setUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setError(null);
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('url', url);

      const response = await fetch('http://localhost:8000/process-youtube', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process video');
      }

      const data = await response.json();
      onShortsGenerated(data.shorts);
    } catch (err) {
      setError('Failed to process video. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center gap-3 mb-4">
        <Video className="w-6 h-6 text-gray-900" />
        <h2 className="text-lg font-semibold text-gray-900">Process YouTube Video</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 mb-1">
            YouTube URL
          </label>
          <input
            id="youtube-url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            disabled={isProcessing}
          />
        </div>

        <Button
          type="submit"
          disabled={!url || isProcessing}
          className="w-full"
        >
          Generate Shorts
        </Button>

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-700 px-4 py-3 rounded-lg">
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        <ProcessingStatus isVisible={isProcessing} />
      </form>
    </div>
  );
}