import React from 'react';

function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold text-gray-900">Job Scraper</h1>
        <p className="mt-2 text-lg text-gray-600">
          Extract structured data from job descriptions using AI
        </p>
      </div>
    </div>
  );
}

export default HomePage;
