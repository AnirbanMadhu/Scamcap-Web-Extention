'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';

export default function QuickScanForm() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiClient.quickScan(url);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to scan URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className=\"max-w-2xl mx-auto p-6\">
      <h2 className=\"text-2xl font-bold mb-4\">Quick URL Scanner</h2>
      
      <form onSubmit={handleScan} className=\"space-y-4\">
        <div>
          <label htmlFor=\"url\" className=\"block text-sm font-medium mb-2\">
            Enter URL to scan
          </label>
          <input
            id=\"url\"
            type=\"url\"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder=\"https://example.com\"
            required
            className=\"w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500\"
          />
        </div>

        <button
          type=\"submit\"
          disabled={loading}
          className=\"w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50\"
        >
          {loading ? 'Scanning...' : 'Scan URL'}
        </button>
      </form>

      {error && (
        <div className=\"mt-4 p-4 bg-red-50 border border-red-200 rounded-lg\">
          <p className=\"text-red-800\">{error}</p>
        </div>
      )}

      {result && (
        <div className=\"mt-6 p-6 bg-white border rounded-lg shadow\">
          <div className={\	ext-lg font-semibold mb-2 \\}>
            {result.is_safe ? ' URL is Safe' : ' Potential Threat Detected'}
          </div>
          
          <div className=\"space-y-2\">
            <p><strong>Risk Score:</strong> {(result.risk_score * 100).toFixed(1)}%</p>
            <p><strong>Risk Level:</strong> {result.risk_level.toUpperCase()}</p>
            
            {result.indicators && result.indicators.length > 0 && (
              <div className=\"mt-4\">
                <strong>Indicators:</strong>
                <ul className=\"list-disc list-inside mt-2 space-y-1\">
                  {result.indicators.map((indicator: string, i: number) => (
                    <li key={i} className=\"text-sm\">{indicator}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
