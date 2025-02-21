import { useState } from 'react';
import { AudioWaveform as Waveform } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AudioPlayer } from './AudioPlayer';
import { AudioUploader } from './AudioUploader';
import { ProcessingStatus } from './ProcessingStatus';
import { reduceNoise } from '@/services/api';

export function NoiseReducer() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [originalAudio, setOriginalAudio] = useState<string | null>(null);
  const [reducedAudio, setReducedAudio] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    try {
      setError(null);
      setIsProcessing(true);
      
      // Create URL for original audio
      const originalUrl = URL.createObjectURL(new Blob([await file.arrayBuffer()], { type: file.type }));
      setOriginalAudio(originalUrl);
      
      // Process and reduce noise
      const reducedUrl = await reduceNoise(file);
      setReducedAudio(reducedUrl);
    } catch (err) {
      setError('Failed to reduce noise. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (reducedAudio) {
      const link = document.createElement('a');
      link.href = reducedAudio;
      link.download = 'reduced_noise.wav';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center gap-3 mb-4">
        <Waveform className="w-6 h-6 text-gray-900" />
        <h2 className="text-lg font-semibold text-gray-900">Noise Reduction</h2>
      </div>

      <div className="space-y-4">
        <AudioUploader onFileSelect={handleFileSelect} isProcessing={isProcessing} />

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-700 px-4 py-3 rounded-lg">
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        <ProcessingStatus isVisible={isProcessing} />

        {(originalAudio || reducedAudio) && (
          <div className="grid gap-4">
            {originalAudio && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-500">Original Audio</h3>
                <AudioPlayer
                  audioUrl={originalAudio}
                  title="Original Recording"
                  className="h-full"
                />
              </div>
            )}
            
            {reducedAudio && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-500">Noise Reduced Audio</h3>
                <AudioPlayer
                  audioUrl={reducedAudio}
                  title="Noise Reduced Recording"
                  onDownload={handleDownload}
                  className="h-full"
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}