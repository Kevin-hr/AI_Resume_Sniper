import { useState, useCallback } from 'react';

interface UseAnalyzeStreamReturn {
  streamedContent: string;
  isStreaming: boolean;
  error: string | null;
  analyzeStream: (formData: FormData) => Promise<void>;
  reset: () => void;
}

export const useAnalyzeStream = (): UseAnalyzeStreamReturn => {
  const [streamedContent, setStreamedContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setStreamedContent('');
    setError(null);
    setIsStreaming(false);
  }, []);

  const analyzeStream = useCallback(async (formData: FormData) => {
    reset();
    setIsStreaming(true);

    try {
      const response = await fetch('/api/analyze_stream', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'Analysis failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // ignore json parse error
        }
        throw new Error(errorMessage);
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported by browser.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        setStreamedContent((prev) => prev + chunk);
      }

    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred during streaming.');
      }
    } finally {
      setIsStreaming(false);
    }
  }, [reset]);

  return {
    streamedContent,
    isStreaming,
    error,
    analyzeStream,
    reset
  };
};
