"use client";

import { useState, ChangeEvent } from "react";
import MatchCircle from "@/components/MatchCircle";
import ThemeToggle from "@/components/ThemeToggle";
import Navbar from "@/components/Navbar";

export default function SimpleMatcher() {
  const [text, setText] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [cvLoaded, setCvLoaded] = useState(false);
  const [matchScore, setMatchScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [cvSummary, setCvSummary] = useState("");
  const [jobSummary, setJobSummary] = useState("");
  const [requiredSkills, setRequiredSkills] = useState<string[]>([]);
  const [preferredSkills, setPreferredSkills] = useState<string[]>([]);
  const [experienceYears, setExperienceYears] = useState<string | null>(null);
  const [educationLevel, setEducationLevel] = useState<string | null>(null);
  const [keyPhrases, setKeyPhrases] = useState<string[]>([]);
  const [overallSimilarity, setOverallSimilarity] = useState<number | null>(null);
  const [sectionSimilarities, setSectionSimilarities] = useState<Record<string, number>>({});
  const [tfidfSimilarity, setTfidfSimilarity] = useState<number | null>(null);
  const [isFallback, setIsFallback] = useState(false);
  const [matchRating, setMatchRating] = useState("");
  const [recommendation, setRecommendation] = useState("");
  const [skillDetails, setSkillDetails] = useState<{
    matched_skills: string[];
    missing_skills: string[];
    extra_skills: string[];
    matched_count: number;
    job_skills_count: number;
    score: number;
  } | null>(null);
  const [strengths, setStrengths] = useState<string[]>([]);
  const [gaps, setGaps] = useState<string[]>([]);
  const [error, setError] = useState("");

  const getBarColor = (value: number) => {
    if (value >= 70) return "bg-emerald-500";
    if (value >= 40) return "bg-amber-500";
    return "bg-red-500";
  };

  const handleCVUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCvFile(file);
      setCvLoaded(true);
    }
  };

  const handleMatch = async () => {
    if (!cvLoaded || !text.trim()) return;
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", cvFile!);
      formData.append("job_description", text);

      const response = await fetch("http://localhost:8000/api/v1/match", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => null);
        setError(err?.detail || "An error occurred while analyzing. Please try again.");
        setMatchScore(null);
        return;
      }

      const result = await response.json();
      console.log(result);

      setMatchScore(result.match_score);
      setCvSummary(result.cv_summary);
      setJobSummary(result.job_summary);
      setRequiredSkills(result.required_skills || []);
      setPreferredSkills(result.preferred_skills || []);
      setExperienceYears(result.experience_years);
      setEducationLevel(result.education_level);
      setKeyPhrases(result.key_phrases || []);
      setOverallSimilarity(result.overall_similarity);
      setSectionSimilarities(result.section_similarities || {});
      setTfidfSimilarity(result.tfidf_similarity);
      setIsFallback(result.is_fallback || false);
      setMatchRating(result.match_rating || "");
      setRecommendation(result.recommendation || "");
      setSkillDetails(result.skill_details || null);
      setStrengths(result.strengths || []);
      setGaps(result.gaps || []);
    } catch {
      setError("Could not connect to the server. Please make sure the backend is running.");
      setMatchScore(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors duration-300">
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
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
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

      <Navbar />

      <main className="max-w-4xl mx-auto px-6 pb-24">
        {/* Hero */}
        <header className="text-center my-16">
          <h1 className="text-5xl font-extrabold tracking-tight mb-4 text-gray-900 dark:text-white">
            Perfect Match
          </h1>
          <p className="text-gray-500 dark:text-gray-400 text-lg">
            Upload your CV and compare it with any job description in seconds.
          </p>
        </header>

        <div className="grid gap-8">
          {/* Card Principal */}
          <div className="bg-white dark:bg-gray-900 rounded-3xl p-8 shadow-md border border-gray-100 dark:border-gray-800 transition-colors">
            <div className="flex flex-col md:flex-row gap-6 mb-8">
              {/* Upload CV */}
              <div className="flex-1">
                <label
                  className={`
                  relative cursor-pointer flex flex-col items-center justify-center p-8 
                  border-2 border-dashed rounded-2xl transition-all
                  ${
                    cvLoaded
                      ? "border-green-300 bg-green-50 dark:bg-green-900/20 dark:border-green-700/50"
                      : "border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 bg-gray-50 dark:bg-gray-800/50"
                  }
                `}
                >
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={handleCVUpload}
                  />
                  <span className="text-3xl mb-2">
                    {cvLoaded ? "✅" : "📄"}
                  </span>
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    {cvLoaded ? cvFile?.name : "upload your resume"}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    PDF o DOCX up to 5MB
                  </p>
                </label>
              </div>

              {/* Match Score */}
              <div className="flex flex-col items-center justify-center px-8 border-l border-gray-100 dark:border-gray-800">
                <MatchCircle percentage={matchScore ?? 0} />
                {matchRating && (
                  <span className={`mt-3 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${
                    matchScore !== null && matchScore >= 90 ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400" :
                    matchScore !== null && matchScore >= 75 ? "bg-lime-100 dark:bg-lime-900/30 text-lime-700 dark:text-lime-400" :
                    matchScore !== null && matchScore >= 60 ? "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400" :
                    matchScore !== null && matchScore >= 40 ? "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400" :
                    "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
                  }`}>
                    {matchRating}
                  </span>
                )}
                {recommendation && (
                  <p className="mt-2 text-xs text-gray-400 dark:text-gray-500 text-center max-w-[180px]">
                    {recommendation}
                  </p>
                )}
              </div>
            </div>

            {/* Textarea */}
            <div className="space-y-4">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300 ml-1">
                Job Description
              </label>
              <textarea
                placeholder="Paste here the job description..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full p-5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl focus:ring-2 focus:ring-blue-500/30 min-h-[200px] resize-none text-gray-700 dark:text-gray-200 transition-all outline-none"
              />
            </div>

            {/* Botón */}
            <button
              onClick={handleMatch}
              disabled={loading || !cvLoaded}
              className="w-full mt-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 dark:disabled:bg-gray-800 disabled:text-gray-400 text-white font-bold rounded-2xl shadow-md transition-all active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
            >
              {loading ? (
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                "Analyze Compatibility"
              )}
            </button>

            {error && (
              <div className="mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
                {error}
              </div>
            )}
          </div>

          {/* Análisis */}
          <div className="grid md:grid-cols-2 gap-6">
            <section className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm min-h-0 transition-colors">
              <h3 className="text-sm font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-4">
                Summary
              </h3>
              <div className="h-24 overflow-y-auto text-gray-400 dark:text-gray-500 italic">
                {matchScore ? (
                  <div className="text-sm text-gray-600 dark:text-gray-300 text-left space-y-2 not-italic">
                    <p>
                      <strong>Job Summary:</strong>
                    </p>
                    <p>{jobSummary}</p>

                    <p className="mt-4">
                      <strong>Candidate Summary:</strong>
                    </p>
                    <p>{cvSummary}</p>
                  </div>
                ) : (
                  "Waiting data..."
                )}
              </div>
            </section>

            <section className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm transition-colors">
              <h3 className="text-sm font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-4">
                Key points
              </h3>
              <div className="h-24 overflow-y-auto text-gray-400 dark:text-gray-500 italic">
                {matchScore ? (
                  <div className="text-sm text-gray-600 dark:text-gray-300 text-left space-y-3 not-italic">
                    <div>
                      <strong>Required Skills:</strong>
                      <p>{requiredSkills.join(", ") || "None detected"}</p>
                    </div>

                    <div>
                      <strong>Preferred Skills:</strong>
                      <p>{preferredSkills.join(", ") || "None detected"}</p>
                    </div>

                    <div>
                      <strong>Experience:</strong>
                      <p>{experienceYears || "Not specified"}</p>
                    </div>

                    <div>
                      <strong>Education:</strong>
                      <p>{educationLevel || "Not specified"}</p>
                    </div>

                    <div>
                      <strong>Key Phrases:</strong>
                      <p>{keyPhrases.join(", ") || "None detected"}</p>
                    </div>
                  </div>
                ) : (
                  "Waiting data..."
                )}
              </div>
            </section>
          </div>

          {/* Score Breakdown */}
          {matchScore !== null && (
            <section className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm transition-colors">
              <h3 className="text-sm font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-6">
                Score Breakdown
              </h3>

              {isFallback && (
                <div className="mb-4 px-4 py-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-xl text-sm text-amber-700 dark:text-amber-400">
                  Limited analysis — only overall and keyword matching available (section breakdown unavailable)
                </div>
              )}

              <div className="space-y-4">
                {/* Overall Semantic */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600 dark:text-gray-300 font-medium">Overall Semantic</span>
                    <span className="text-gray-500 dark:text-gray-400">{overallSimilarity ?? 0}%</span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full transition-all ${getBarColor(overallSimilarity ?? 0)}`}
                      style={{ width: `${Math.min(overallSimilarity ?? 0, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Section-level bars (hidden in fallback mode) */}
                {!isFallback && (
                  <>
                    {/* Skills Match */}
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600 dark:text-gray-300 font-medium">Skills Match</span>
                        <span className="text-gray-500 dark:text-gray-400">{sectionSimilarities.skills_semantic ?? 0}%</span>
                      </div>
                      <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5">
                        <div
                          className={`h-2.5 rounded-full transition-all ${getBarColor(sectionSimilarities.skills_semantic ?? 0)}`}
                          style={{ width: `${Math.min(sectionSimilarities.skills_semantic ?? 0, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Experience Relevance */}
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600 dark:text-gray-300 font-medium">Experience Relevance</span>
                        <span className="text-gray-500 dark:text-gray-400">{sectionSimilarities.experience ?? 0}%</span>
                      </div>
                      <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5">
                        <div
                          className={`h-2.5 rounded-full transition-all ${getBarColor(sectionSimilarities.experience ?? 0)}`}
                          style={{ width: `${Math.min(sectionSimilarities.experience ?? 0, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Education Alignment */}
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600 dark:text-gray-300 font-medium">Education Alignment</span>
                        <span className="text-gray-500 dark:text-gray-400">{sectionSimilarities.education ?? 0}%</span>
                      </div>
                      <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5">
                        <div
                          className={`h-2.5 rounded-full transition-all ${getBarColor(sectionSimilarities.education ?? 0)}`}
                          style={{ width: `${Math.min(sectionSimilarities.education ?? 0, 100)}%` }}
                        />
                      </div>
                    </div>
                  </>
                )}

                {/* Keyword Match (TF-IDF) */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600 dark:text-gray-300 font-medium">Keyword Match</span>
                    <span className="text-gray-500 dark:text-gray-400">{tfidfSimilarity ?? 0}%</span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full transition-all ${getBarColor(tfidfSimilarity ?? 0)}`}
                      style={{ width: `${Math.min(tfidfSimilarity ?? 0, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Skill Details */}
          {matchScore !== null && skillDetails && !isFallback && (
            <section className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm transition-colors">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-sm font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  Skill Analysis
                </h3>
                <span className="text-sm font-semibold text-gray-500 dark:text-gray-400">
                  {skillDetails.matched_count}/{skillDetails.job_skills_count} skills matched
                </span>
              </div>

              {skillDetails.matched_skills.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-500 uppercase tracking-wide mb-2">Matched Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {skillDetails.matched_skills.map((skill: string) => (
                      <span key={skill} className="px-3 py-1 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 text-xs font-medium rounded-full border border-emerald-200 dark:border-emerald-800/50">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {skillDetails.missing_skills.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-red-500 dark:text-red-400 uppercase tracking-wide mb-2">Missing Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {skillDetails.missing_skills.map((skill: string) => (
                      <span key={skill} className="px-3 py-1 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-xs font-medium rounded-full border border-red-200 dark:border-red-800/50">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </section>
          )}

          {/* Strengths & Gaps */}
          {matchScore !== null && (strengths.length > 0 || gaps.length > 0) && (
            <div className="grid md:grid-cols-2 gap-6">
              {strengths.length > 0 && (
                <section className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm transition-colors">
                  <h3 className="text-sm font-bold text-emerald-500 uppercase tracking-wider mb-4">
                    Strengths
                  </h3>
                  <ul className="space-y-2">
                    {strengths.map((item, i) => (
                      <li key={i} className="text-sm text-gray-600 dark:text-gray-300 flex items-start gap-2">
                        <span className="text-emerald-500 mt-0.5">+</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {gaps.length > 0 && (
                <section className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm transition-colors">
                  <h3 className="text-sm font-bold text-orange-500 uppercase tracking-wider mb-4">
                    Gaps
                  </h3>
                  <ul className="space-y-2">
                    {gaps.map((item, i) => (
                      <li key={i} className="text-sm text-gray-600 dark:text-gray-300 flex items-start gap-2">
                        <span className="text-orange-500 mt-0.5">-</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </section>
              )}
            </div>
          )}
        </div>

        {/* Footer Note */}
        <div className="mt-20 pt-12 border-t border-slate-100 dark:border-gray-800">
          <p className="text-center text-xs text-slate-400 dark:text-gray-500 tracking-wide">
            Analysis generated through natural language processing · The results
            are indicative and do not replace human evaluation
          </p>
        </div>
      </main>
    </div>
  );
}
