import { Loader2 } from 'lucide-react';

interface ProcessingStatusProps {
  isVisible: boolean;
}

export function ProcessingStatus({ isVisible }: ProcessingStatusProps) {
  if (!isVisible) return null;

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-gray-200 rounded-full animate-spin">
          <div className="absolute top-0 left-0 w-12 h-12 border-4 border-gray-900 rounded-full animate-spin-fast border-t-transparent" />
        </div>
      </div>
      <p className="mt-4 text-sm text-gray-600 font-medium">
        Enhancing your audio...
      </p>
      <p className="mt-1 text-xs text-gray-500">
        This may take a few moments
      </p>
    </div>
  );
}