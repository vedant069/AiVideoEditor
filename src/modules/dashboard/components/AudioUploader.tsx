import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileAudio } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AudioUploaderProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

export function AudioUploader({ onFileSelect, isProcessing }: AudioUploaderProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.m4a', '.aac'],
    },
    maxFiles: 1,
    disabled: isProcessing,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative border-2 border-dashed rounded-xl p-12 transition-colors",
        isDragActive ? "border-gray-400 bg-gray-50" : "border-gray-200",
        isProcessing ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:border-gray-300"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        <div className="p-4 bg-gray-50 rounded-full">
          {isDragActive ? (
            <FileAudio className="w-10 h-10 text-gray-600" />
          ) : (
            <Upload className="w-10 h-10 text-gray-600" />
          )}
        </div>
        <div className="text-center">
          <p className="text-base font-medium text-gray-700">
            {isDragActive ? 'Drop your audio file here' : 'Upload your audio file'}
          </p>
          <p className="mt-1 text-sm text-gray-500">
            Drag and drop or click to select
          </p>
          <p className="mt-2 text-xs text-gray-400">
            Supports WAV, MP3, M4A, or AAC
          </p>
        </div>
      </div>
    </div>
  );
}