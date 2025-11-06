// app/page.js
'use client';
import { useState } from 'react';

export default function Home() {
  const [inputText, setInputText] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisType, setAnalysisType] = useState('qualification');

  const analyzeLead = async () => {
    if (!inputText.trim()) {
      alert('Please enter some lead information');
      return;
    }

    setLoading(true);
    setAnalysis('');

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          analysisType: analysisType
        })
      });

      const data = await response.json();

      if (response.ok) {
        setAnalysis(data.analysis);
      } else {
        throw new Error(data.error || 'Failed to analyze');
      }
    } catch (error) {
      console.error('Error:', error);
      setAnalysis('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            ACU Lead Finder AI
          </h1>
          <p className="text-gray-600">
            AI-powered lead analysis and qualification
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Type
            </label>
            <select
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="qualification">Lead Qualification</option>
              <option value="scoring">Lead Scoring</option>
              <option value="intent">Intent Analysis</option>
              <option value="followup">Follow-up Strategy</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lead Information
            </label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste lead information, contact details, company info, or conversation history here..."
              rows="8"
              className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <button
            onClick={analyzeLead}
            disabled={loading || !inputText.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Analyzing...
              </div>
            ) : (
              'Analyze Lead'
            )}
          </button>
        </div>

        {analysis && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Analysis Results
            </h2>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                {analysis}
              </div>
            </div>
          </div>
        )}

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white rounded-xl shadow-md p-6 text-center">
            <div className="text-blue-600 text-2xl mb-2">🔍</div>
            <h3 className="font-semibold text-gray-800 mb-2">Lead Qualification</h3>
            <p className="text-gray-600 text-sm">Automatically qualify leads based on intent and fit</p>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6 text-center">
            <div className="text-green-600 text-2xl mb-2">📊</div>
            <h3 className="font-semibold text-gray-800 mb-2">Scoring & Ranking</h3>
            <p className="text-gray-600 text-sm">Score leads by potential and priority</p>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6 text-center">
            <div className="text-purple-600 text-2xl mb-2">💡</div>
            <h3 className="font-semibold text-gray-800 mb-2">Actionable Insights</h3>
            <p className="text-gray-600 text-sm">Get specific follow-up recommendations</p>
          </div>
        </div>
      </div>
    </div>
  );
}
