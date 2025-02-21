import { useState } from 'react';
import { Wand2 } from 'lucide-react';
import { AudioUploader } from './components/AudioUploader';
import { AudioPlayer } from './components/AudioPlayer';
import { ProcessingStatus } from './components/ProcessingStatus';
import { YoutubeProcessor } from './components/YoutubeProcessor';
import { NoiseReducer } from './components/NoiseReducer';
import { ShortVideo } from './components/ShortVideo';
import { enhanceAudio } from '@/services/api';
// import { LampDemo } from '@/components/ui/lamp';

interface Short {
  url: string;
  script: string;
}

export function DashboardPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [originalAudio, setOriginalAudio] = useState<string | null>(null);
  const [enhancedAudio, setEnhancedAudio] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [shorts, setShorts] = useState<Short[]>([]);

  const handleFileSelect = async (file: File) => {
    try {
      setError(null);
      setIsProcessing(true);

      // Create URL for original audio
      const originalUrl = URL.createObjectURL(new Blob([await file.arrayBuffer()], { type: file.type }));
      setOriginalAudio(originalUrl);

      // Process and enhance audio
      const enhancedUrl = await enhanceAudio(file);
      setEnhancedAudio(enhancedUrl);
    } catch (err) {
      setError('Failed to process audio. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (enhancedAudio) {
      const link = document.createElement('a');
      link.href = enhancedAudio;
      link.download = 'enhanced_audio.wav';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleShortsGenerated = (newShorts: Short[]) => {
    setShorts(newShorts);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <div className="inline-flex items-center justify-center gap-3 mb-4 px-4 py-2 bg-white rounded-full shadow-sm">
            <Wand2 className="w-6 h-6 text-gray-900" />
            <h1 className="text-xl font-semibold text-gray-900">Content Enhancer</h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Enhance your audio files, reduce noise, or convert YouTube videos into engaging shorts.
            Our AI helps you create better content by improving quality and removing unwanted elements.
          </p>
        </header>

        <div className="grid gap-8">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Audio Enhancement</h2>
                <AudioUploader onFileSelect={handleFileSelect} isProcessing={isProcessing} />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-100 text-red-700 px-4 py-3 rounded-lg">
                  <p className="text-sm font-medium">{error}</p>
                </div>
              )}

              <ProcessingStatus isVisible={isProcessing} />

              {(originalAudio || enhancedAudio) && (
                <div className="grid gap-6">
                  {originalAudio && (
                    <div className="space-y-2">
                      <h2 className="text-sm font-medium text-gray-500">Original Audio</h2>
                      <AudioPlayer
                        audioUrl={originalAudio}
                        title="Original Recording"
                        className="h-full"
                      />
                    </div>
                  )}

                  {enhancedAudio && (
                    <div className="space-y-2">
                      <h2 className="text-sm font-medium text-gray-500">Enhanced Audio</h2>
                      <AudioPlayer
                        audioUrl={enhancedAudio}
                        title="Enhanced Recording"
                        onDownload={handleDownload}
                        className="h-full"
                      />
                    </div>
                  )}
                </div>
              )}

              <NoiseReducer />
            </div>

            <div className="space-y-6">
              <YoutubeProcessor onShortsGenerated={handleShortsGenerated} />

              {shorts.length > 0 && (
                <div className="grid gap-6">
                  <h2 className="text-lg font-semibold text-gray-900">Generated Shorts</h2>
                  <div className="grid sm:grid-cols-2 gap-6">
                    {shorts.map((short, index) => (
                      <ShortVideo
                        key={index}
                        videoUrl={short.url}
                        script={short.script}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}