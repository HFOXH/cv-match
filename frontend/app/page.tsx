"use client";

import { useState, useEffect } from "react";
import MatchCircle from "@/components/MatchCircle";

export default function SimpleMatcher() {
  const [text, setText] = useState("");
  const [cvFile, setCvFile] = useState(null);
  const [cvLoaded, setCvLoaded] = useState(false);
  const [matchScore, setMatchScore] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCVUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setCvFile(file);
      setCvLoaded(true);
    }
  };

  const handleMatch = async () => {
    if (!cvLoaded || !text) return;
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cv_text: text, job_text: text }),
      });
      const result = await response.json();
      setMatchScore(result.match_percentage);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900 selection:bg-blue-100">
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }

        .animate-fade-in-up {
          animation: fadeInUp 0.6s ease-out forwards;
        }

        .animate-float {
          animation: float 6s ease-in-out infinite;
        }

        .upload-area {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .upload-area:hover {
          transform: translateY(-2px);
        }
      `}</style>

      {/* Minimal Header */}
      <nav className="border-b border-slate-100 mb-4">
        <div className="max-w-6xl mx-auto px-8 py-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-1.5 h-8 bg-slate-950 rounded-full" />
            <span className="text-lg font-bold tracking-tight">CVMatch</span>
          </div>
          <div className="flex items-center gap-6">
            <button className="text-sm text-slate-500 hover:text-slate-950 transition-colors font-medium">
              Documentation
            </button>
            <button className="text-sm text-slate-500 hover:text-slate-950 transition-colors font-medium">
              Support
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 pb-24">
        
        {/* Hero */}
        <header className="text-center mb-16">
          <h1 className="text-5xl font-extrabold tracking-tight mb-4 text-gray-900">
            Perfect Match
          </h1>
          <p className="text-gray-500 text-lg">
            Upload your CV and compare it with any job description in seconds.
          </p>
        </header>

        <div className="grid gap-8">
          
          {/* Card Principal */}
          <div className="bg-white rounded-3xl p-8 shadow-md border border-gray-100">
            
            <div className="flex flex-col md:flex-row gap-6 mb-8">
              
              {/* Upload CV */}
              <div className="flex-1">
                <label className={`
                  relative cursor-pointer flex flex-col items-center justify-center p-8 
                  border-2 border-dashed rounded-2xl transition-all
                  ${cvLoaded 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-200 hover:border-blue-400 bg-gray-50'}
                `}>
                  <input type="file" className="hidden" onChange={handleCVUpload} />
                  <span className="text-3xl mb-2">{cvLoaded ? "✅" : "📄"}</span>
                  <p className="text-sm font-semibold text-gray-700">
                    {cvLoaded ? cvFile.name : "upload your resume"}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">PDF o DOCX up to 5MB</p>
                </label>
              </div>

              {/* Match Score */}
              <div className="flex flex-col items-center justify-center px-8 border-l border-gray-100">
                <MatchCircle percentage={matchScore ?? 0} size={120} />
                <p className="mt-4 text-sm font-medium text-gray-400 uppercase tracking-widest">Match Score</p>
              </div>
            </div>

            {/* Textarea */}
            <div className="space-y-4">
              <label className="text-sm font-semibold text-gray-700 ml-1">
                Job Description
              </label>
              <textarea
                placeholder="Paste here the job description..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full p-5 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500/30 min-h-[200px] resize-none text-gray-700 transition-all"
              />
            </div>

            {/* Botón */}
            <button
              onClick={handleMatch}
              disabled={loading || !cvLoaded}
              className="w-full mt-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 text-white font-bold rounded-2xl shadow-md transition-all active:scale-[0.98] flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                "Analyze Compatibility"
              )}
            </button>
          </div>

          {/* Análisis */}
          <div className="grid md:grid-cols-2 gap-6">
            <section className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Summary</h3>
              <div className="h-24 flex items-center justify-center text-gray-400 italic">
                {matchScore ? "Analysis successfully generated." : "Waiting data..."}
              </div>
            </section>
            
            <section className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Key points</h3>
              <div className="h-24 flex items-center justify-center text-gray-400 italic">
                {matchScore ? "3 strengths identified." : "Waiting data..."}
              </div>
            </section>
          </div>

        </div>

        {/* Footer Note */}
        <div className="mt-20 pt-12 border-t border-slate-100">
          <p className="text-center text-xs text-slate-400 tracking-wide">
            Analysis generated through natural language processing · The results are indicative and do not replace human evaluation
          </p>
        </div>
      </main>
    </div>
  );
}
