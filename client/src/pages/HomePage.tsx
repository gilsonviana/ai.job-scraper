import React, { useState } from 'react';
import useExtraction from '../hooks/useExtraction';

function HomePage() {
  const [extractionSource, setExtractionSource] = useState<'url' | 'pdf'>('url');
  const [urlInput, setUrlInput] = useState('');
  const [fileInput, setFileInput] = useState<File | null>(null);
  const { loading, error, result, extract } = useExtraction();

  const handleExtract = async () => {
    if (extractionSource === 'url') {
      await extract({ source: 'url', url: urlInput });
    } else if (extractionSource === 'pdf' && fileInput) {
      await extract({ source: 'pdf', file: fileInput });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold text-gray-900">Job Scraper</h1>
        <p className="mt-2 text-lg text-gray-600">
          Extract structured data from job descriptions using AI
        </p>

        <div className="mt-12 rounded-lg bg-white p-8 shadow">
          <div className="mb-6">
            <label className="mb-4 block text-sm font-medium text-gray-700">
              Source Type
            </label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="url"
                  checked={extractionSource === 'url'}
                  onChange={(e) =>
                    setExtractionSource(e.target.value as 'url' | 'pdf')
                  }
                  className="mr-2"
                />
                <span>URL</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="pdf"
                  checked={extractionSource === 'pdf'}
                  onChange={(e) =>
                    setExtractionSource(e.target.value as 'url' | 'pdf')
                  }
                  className="mr-2"
                />
                <span>PDF File</span>
              </label>
            </div>
          </div>

          {extractionSource === 'url' ? (
            <div className="mb-6">
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Job Posting URL
              </label>
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://example.com/job-posting"
                className="w-full rounded border border-gray-300 px-4 py-2"
              />
            </div>
          ) : (
            <div className="mb-6">
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Upload PDF
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFileInput(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:rounded file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
          )}

          <button
            onClick={handleExtract}
            disabled={loading}
            className="w-full rounded bg-blue-600 px-4 py-2 text-white font-semibold hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Extracting...' : 'Extract Job Data'}
          </button>

          {error && (
            <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-700">
              <p className="font-semibold">{error.code}</p>
              <p>{error.message}</p>
            </div>
          )}

          {result && (
            <div className="mt-6 space-y-4 rounded-lg bg-green-50 p-6">
              <h2 className="text-2xl font-bold text-green-900">
                {result.job_title}
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-green-700">Location</p>
                  <p className="text-lg text-green-900">{result.location}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-green-700">
                    Seniority Level
                  </p>
                  <p className="text-lg text-green-900">
                    {result.seniority_level || 'Not specified'}
                  </p>
                </div>
                {result.salary_min && (
                  <div>
                    <p className="text-sm font-medium text-green-700">
                      Salary Range
                    </p>
                    <p className="text-lg text-green-900">
                      ${result.salary_min.toLocaleString()} - $
                      {result.salary_max?.toLocaleString()}
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium text-green-700">
                    Remote Policy
                  </p>
                  <p className="text-lg text-green-900">
                    {result.remote_policy || 'Not specified'}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-green-700">
                  Tech Stack
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.required_stack.map((tech) => (
                    <span
                      key={tech}
                      className="rounded-full bg-green-200 px-3 py-1 text-sm text-green-900"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-green-700">
                  Key Responsibilities
                </p>
                <ul className="mt-2 list-inside list-disc space-y-1">
                  {result.key_responsibilities.map((resp, idx) => (
                    <li key={idx} className="text-green-900">
                      {resp}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex items-center justify-between">
                <p className="text-sm text-green-700">
                  Confidence Score: {(result.confidence_score * 100).toFixed(1)}
                  %
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default HomePage;
