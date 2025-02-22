import { useState, useEffect, useRef } from 'react';
import { Wand2, Music, Youtube, Volume2, Video, Edit3 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { AudioUploader } from './components/AudioUploader';
import { AudioPlayer } from './components/AudioPlayer';
import { ProcessingStatus } from './components/ProcessingStatus';
import { YoutubeProcessor } from './components/YoutubeProcessor';
import { NoiseReducer } from './components/NoiseReducer';
import { ShortVideo } from './components/ShortVideo';
import { VideoHighlighter } from './components/VideoHighlighter';
import { VideoEditor } from './components/VideoEditor';
import { Navbar } from '@/components/ui/Navbar';
import { enhanceAudio } from '@/services/api';
import { AuroraBackground } from '@/components/ui/aurora-background';
import '@/styles/animations.css';

interface Short {
  url: string;
  script: string;
}

type FeatureType = 'audio' | 'youtube' | 'noise' | 'highlight' | 'edit' | null;

const features = [
  {
    id: 'audio',
    title: 'Audio Enhancement',
    description: 'Enhance your audio files with AI-powered processing',
    icon: Music,
    gradient: 'from-purple-600/20 to-pink-600/20',
    borderGlow: 'group-hover:shadow-purple-500/50',
    iconClass: 'text-purple-400',
  },
  {
    id: 'youtube',
    title: 'Process YouTube Video',
    description: 'Convert YouTube videos into engaging short-form content',
    icon: Youtube,
    gradient: 'from-red-600/20 to-orange-600/20',
    borderGlow: 'group-hover:shadow-red-500/50',
    iconClass: 'text-red-400',
  },
  {
    id: 'noise',
    title: 'Noise Reduction',
    description: 'Remove background noise and enhance audio clarity',
    icon: Volume2,
    gradient: 'from-blue-600/20 to-cyan-600/20',
    borderGlow: 'group-hover:shadow-blue-500/50',
    iconClass: 'text-blue-400',
  },
  {
    id: 'highlight',
    title: 'Video Highlighter',
    description: 'Automatically detect and highlight key moments in your videos',
    icon: Video,
    gradient: 'from-green-600/20 to-emerald-600/20',
    borderGlow: 'group-hover:shadow-green-500/50',
    iconClass: 'text-green-400',
  },
  {
    id: 'edit',
    title: 'Video Editor',
    description: 'Professional video editing tools with AI assistance',
    icon: Edit3,
    gradient: 'from-yellow-600/20 to-amber-600/20',
    borderGlow: 'group-hover:shadow-yellow-500/50',
    iconClass: 'text-yellow-400',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: {
      staggerChildren: 0.3
    }
  },
  exit: {
    opacity: 0,
    transition: {
      when: "beforeChildren",
      staggerChildren: 0.1,
      staggerDirection: -1
    }
  }
};

const featureCardVariants = {
  hidden: { y: 50, opacity: 0 },
  visible: { 
    y: 0, 
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 12
    }
  },
  exit: { 
    y: -50, 
    opacity: 0,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 12
    }
  },
  hover: {
    y: -8,
    scale: 1.02,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 10
    }
  }
};

const pageTransitionVariants = {
  initial: {
    opacity: 0,
    scale: 0.9,
    filter: "blur(10px)"
  },
  animate: {
    opacity: 1,
    scale: 1,
    filter: "blur(0px)",
    transition: {
      duration: 0.5,
      ease: "easeOut"
    }
  },
  exit: {
    opacity: 0,
    scale: 1.1,
    filter: "blur(10px)",
    transition: {
      duration: 0.5,
      ease: "easeIn"
    }
  }
};

export function DashboardPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [originalAudio, setOriginalAudio] = useState<string | null>(null);
  const [enhancedAudio, setEnhancedAudio] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [shorts, setShorts] = useState<Short[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<FeatureType>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const backgroundRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleVideoSelect = (file: File) => {
    setSelectedVideo(file);
  };

  const handleFileSelect = async (file: File) => {
    try {
      setError(null);
      setIsProcessing(true);
      const originalUrl = URL.createObjectURL(file);
      setOriginalAudio(originalUrl);
      const enhancedUrl = await enhanceAudio(file);
      setEnhancedAudio(enhancedUrl);
    } catch (err) {
      setError('Failed to process audio. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleShortsGenerated = (newShorts: Short[]) => {
    setShorts(newShorts);
  };

  const handleFeatureSelect = (feature: FeatureType) => {
    setSelectedFeature(feature);
    setError(null);
  };

  const handleBack = () => {
    setSelectedFeature(null);
    setSelectedVideo(null);
    setError(null);
  };

  const renderFeatureContent = () => {
    const feature = features.find(f => f.id === selectedFeature);
    if (!feature) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-8"
      >
        <div className="bg-gray-800/30 backdrop-blur-md rounded-2xl shadow-xl border border-gray-400/20 p-8 relative overflow-hidden group">
          <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
          <div className={`absolute -inset-px bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 blur-sm transition-all duration-500 ${feature.borderGlow}`} />
          <div className="relative z-10">
            {selectedFeature === 'audio' && (
              <>
                <h2 className="text-2xl font-semibold text-white mb-6">Audio Enhancement</h2>
                <AudioUploader onFileSelect={handleFileSelect} isProcessing={isProcessing} />
                {error && (
                  <div className="mt-4 bg-red-900/20 border border-red-500/30 text-red-400 px-6 py-4 rounded-xl">
                    <p className="text-sm font-medium">{error}</p>
                  </div>
                )}
                <ProcessingStatus isVisible={isProcessing} />
                {(originalAudio || enhancedAudio) && (
                  <div className="mt-8 space-y-8">
                    {originalAudio && (
                      <div className="bg-gray-800/30 backdrop-blur-md rounded-2xl p-6 border border-gray-400/20">
                        <h3 className="text-lg font-medium text-white mb-4">Original Audio</h3>
                        <AudioPlayer audioUrl={originalAudio} title="Original Recording" />
                      </div>
                    )}
                    {enhancedAudio && (
                      <div className="bg-gray-800/30 backdrop-blur-md rounded-2xl p-6 border border-gray-400/20">
                        <h3 className="text-lg font-medium text-white mb-4">Enhanced Audio</h3>
                        <AudioPlayer audioUrl={enhancedAudio} title="Enhanced Recording" />
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
            {selectedFeature === 'youtube' && (
              <>
                <h2 className="text-2xl font-semibold text-white mb-6">YouTube Video Processing</h2>
                <YoutubeProcessor onShortsGenerated={handleShortsGenerated} />
                {shorts.length > 0 && (
                  <div className="mt-8 grid gap-6">
                    {shorts.map((short, index) => (
                      <ShortVideo key={index} url={short.url} script={short.script} />
                    ))}
                  </div>
                )}
              </>
            )}
            {selectedFeature === 'noise' && (
              <>
                <h2 className="text-2xl font-semibold text-white mb-6">Noise Reduction</h2>
                <NoiseReducer />
              </>
            )}
            {selectedFeature === 'highlight' && (
              <>
                <h2 className="text-2xl font-semibold text-white mb-6">Video Highlighter</h2>
                <VideoHighlighter 
                  selectedVideo={selectedVideo}
                  onVideoSelect={setSelectedVideo}
                />
              </>
            )}
            {selectedFeature === 'edit' && (
              <>
                <h2 className="text-2xl font-semibold text-white mb-6">Video Editor</h2>
                <VideoEditor 
                  selectedVideo={selectedVideo}
                  onVideoSelect={setSelectedVideo}
                />
              </>
            )}
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <AuroraBackground>
        <Navbar isExpanded={selectedFeature !== null} />
        <AnimatePresence mode="wait">
          {!selectedFeature ? (
            <motion.div
              key="feature-selection"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="max-w-7xl mx-auto px-4 py-12 relative z-10"
            >
              <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-8"
              >
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="inline-flex items-center justify-center gap-3 mb-3 px-6 py-3 bg-gray-800/30 
                    backdrop-blur-md rounded-full shadow-lg border border-gray-400/20 relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-blue-500/20 to-pink-500/20 animate-gradient-x" />
                  <Wand2 className="w-5 h-5 text-gray-300 relative z-10" />
                  <h1 className="text-xl font-semibold text-white relative z-10">
                    Content Enhancer
                  </h1>
                </motion.div>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="text-gray-300 max-w-2xl mx-auto leading-relaxed text-sm"
                >
                  Transform your content with our AI-powered tools
                </motion.p>
              </motion.header>

              <motion.div className="flex flex-wrap justify-center items-center gap-3 max-w-4xl mx-auto px-4">
                {features.map((feature) => (
                  <motion.button
                    key={feature.id}
                    variants={featureCardVariants}
                    whileHover="hover"
                    onClick={() => handleFeatureSelect(feature.id as FeatureType)}
                    className={`group relative bg-gray-800/30 backdrop-blur-md rounded-lg p-3 text-left border border-gray-400/20 
                      transition-all duration-500 hover:border-gray-400/40 overflow-hidden flex items-center gap-3
                      w-[220px] h-[64px]`}
                  >
                    {/* Animated gradient background */}
                    <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 
                      group-hover:opacity-100 transition-opacity duration-500`} />
                    
                    {/* Glowing border effect */}
                    <div className={`absolute -inset-px bg-gradient-to-r from-transparent via-white/5 to-transparent 
                      opacity-0 group-hover:opacity-100 blur-sm transition-all duration-500 ${feature.borderGlow}`} />
                    
                    <div className="relative z-10 flex items-center gap-3 w-full">
                      <div className={`flex-shrink-0 p-1.5 rounded-lg bg-gray-700/50 
                        transform group-hover:scale-110 transition-transform duration-500`}>
                        <feature.icon className={`w-4 h-4 ${feature.iconClass}`} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="text-sm font-medium text-white truncate">{feature.title}</h3>
                        <p className="text-gray-300 text-xs leading-tight truncate">{feature.description}</p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </motion.div>
            </motion.div>
          ) : (
            <motion.div
              key="feature-content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ 
                duration: 0.8,
                ease: [0.4, 0, 0.2, 1],
                delay: 0.2
              }}
              className="max-w-7xl mx-auto px-4 pt-24 pb-12 relative z-10"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleBack}
                className="mb-8 inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gray-800/30 
                  backdrop-blur-md border border-gray-400/20 hover:border-gray-400/40 
                  transition-all duration-300 text-gray-300 hover:text-white"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                    clipRule="evenodd"
                  />
                </svg>
                Return to Dashboard
              </motion.button>
              {renderFeatureContent()}
            </motion.div>
          )}
        </AnimatePresence>
      </AuroraBackground>
    </div>
  );
}