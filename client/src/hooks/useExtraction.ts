import { useState, useCallback } from 'react';
import apiClient from '../services/apiClient';
import { JobExtractionResponse, ErrorDetail, ExtractRequest } from '../services/types';

interface UseExtractionReturn {
  loading: boolean;
  error: ErrorDetail | null;
  result: JobExtractionResponse | null;
  extract: (request: ExtractRequest) => Promise<void>;
  reset: () => void;
}

export const useExtraction = (): UseExtractionReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorDetail | null>(null);
  const [result, setResult] = useState<JobExtractionResponse | null>(null);

  const extract = useCallback(async (request: ExtractRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (request.source === 'url') {
        if (!request.url) {
          setError({
            code: 'MISSING_URL',
            message: 'URL is required',
            details: {},
          });
          return;
        }

        const response = await apiClient.post('/extract', {
          source: 'url',
          url: request.url,
        });

        if (response.data.error) {
          setError(response.data.error);
        } else {
          setResult(response.data.data);
        }
      } else if (request.source === 'pdf') {
        if (!request.file) {
          setError({
            code: 'MISSING_FILE',
            message: 'File is required',
            details: {},
          });
          return;
        }

        const formData = new FormData();
        formData.append('source', 'pdf');
        formData.append('file', request.file);

        const response = await apiClient.post('/extract', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.error) {
          setError(response.data.error);
        } else {
          setResult(response.data.data);
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError({
          code: 'INTERNAL_ERROR',
          message: err.message || 'An error occurred',
          details: {},
        });
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setResult(null);
  }, []);

  return { loading, error, result, extract, reset };
};

export default useExtraction;
