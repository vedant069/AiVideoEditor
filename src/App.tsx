import { useState } from 'react';
import { Wand2 } from 'lucide-react';
import { Dropzone } from './components/dropzone';
import { AudioPlayer } from './components/audio-player';
import { Button } from './components/ui/button';
import { enhanceAudio } from './services/api';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [originalAudio, setOriginalAudio] = useState<string | null>(null);
  const [enhancedAudio, setEnhancedAudio] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    try {
      setError(null);
      setEnhancedAudio(null); // Clear previous enhanced audio
      setIsProcessing(true);
      
      // Create URL for original audio
      const originalUrl = URL.createObjectURL(file);
      setOriginalAudio(originalUrl);
      
      // Process and enhance audio
      const enhancedUrl = await enhanceAudio(file);
      setEnhancedAudio(enhancedUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process audio. Please try again.');
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Wand2 className="w-8 h-8 text-gray-900" />
            <h1 className="text-3xl font-bold text-gray-900">Audio Enhancer</h1>
          </div>
          <p className="text-gray-600">
            Upload your audio file and let our AI enhance it for crystal-clear quality
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <Dropzone onFileSelect={handleFileSelect} />
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-8">
            {error}
          </div>
        )}

        {isProcessing && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4" />
            <p className="text-gray-600">Enhancing your audio...</p>
          </div>
        )}

        {(originalAudio || enhancedAudio) && (
          <div className="grid md:grid-cols-2 gap-8">
            {originalAudio && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">Original Audio</h2>
                <AudioPlayer audioUrl={originalAudio} title="Original Recording" />
              </div>
            )}
            
            {enhancedAudio && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">Enhanced Audio</h2>
                <AudioPlayer audioUrl={enhancedAudio} title="Enhanced Recording" />
                <Button onClick={handleDownload} className="w-full">
                  Download Enhanced Audio
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;