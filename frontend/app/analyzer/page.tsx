"use client";

import { useState, ChangeEvent } from "react";
import Navbar from "@/components/Navbar";
import Paywall from "@/components/Paywall";
import Footer from "@/components/Footer";

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
    if (value >= 70) return "#10B981";
    if (value >= 40) return "#F59E0B";
    return "#EF4444";
  };

  const getRatingClasses = (score: number | null) => {
    if (score === null) return "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-600";
    if (score >= 90) return "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-700";
    if (score >= 75) return "bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 border-green-200 dark:border-green-700";
    if (score >= 60) return "bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-700";
    if (score >= 40) return "bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-400 border-orange-200 dark:border-orange-700";
    return "bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-400 border-red-200 dark:border-red-700";
  };

  const getCircleStroke = (score: number | null) => {
    if (score === null) return "#D1D5DB";
    if (score >= 70) return "#10B981";
    if (score >= 40) return "#F59E0B";
    return "#EF4444";
  };

  const circumference = 2 * Math.PI * 26;
  const dashOffset = matchScore !== null
    ? circumference - (matchScore / 100) * circumference
    : circumference;

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

  const BarRow = ({ label, value }: { label: string; value: number }) => (
    <div className="mb-3 last:mb-0">
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-gray-500 dark:text-gray-400">{label}</span>
        <span className="font-semibold" style={{ color: getBarColor(value) }}>{value}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${Math.min(value, 100)}%`, background: getBarColor(value) }}
        />
      </div>
    </div>
  );

  const StatCard = ({ label, value, sublabel }: { label: string; value: number; sublabel?: string }) => (
    <div className="bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-2xl p-4 flex flex-col gap-1">
      <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-3xl font-extrabold tracking-tight" style={{ color: getBarColor(value) }}>
        {value}%
      </p>
      {sublabel && <p className="text-xs text-gray-400 dark:text-gray-500">{sublabel}</p>}
    </div>
  );

  return (
    <Paywall>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 antialiased overflow-x-hidden transition-colors duration-300">
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
          *, *::before, *::after { box-sizing: border-box; }
          body { font-family: 'Inter', sans-serif; }

          .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #DBEAFE;
            color: #1D4ED8;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            padding: 4px 14px;
            border-radius: 999px;
            border: 1px solid #BFDBFE;
          }
          .dark .pill {
            background: #1E3A8A;
            color: #93C5FD;
            border-color: #1D4ED8;
          }

          .btn-primary {
            background: #2563EB;
            color: #fff;
            font-weight: 600;
            transition: background 0.18s, transform 0.14s, box-shadow 0.18s;
            box-shadow: 0 2px 0 #1D4ED8;
          }
          .btn-primary:hover:not(:disabled) { background: #1D4ED8; transform: translateY(-1px); box-shadow: 0 4px 0 #1E40AF; }
          .btn-primary:active:not(:disabled) { transform: translateY(1px); box-shadow: 0 1px 0 #1E40AF; }

          .card-hover { transition: transform 0.22s ease, box-shadow 0.22s ease; }
          .card-hover:hover { transform: translateY(-2px); box-shadow: 0 14px 28px -8px rgba(37,99,235,0.12); }

          @keyframes spin { to { transform: rotate(360deg); } }
          .spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block; }
        `}</style>

        <Navbar />

        <main className="max-w-4xl mx-auto px-6 pb-24">

          <header className="text-center my-16">
            <div className="pill mb-5 inline-flex">✦ AI-Powered Analysis</div>
            <h1 className="text-5xl font-extrabold tracking-tight mb-4 text-gray-900 dark:text-white">
              Perfect Match
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              Upload your CV and compare it with any job description in seconds.
            </p>
          </header>

          <div className="flex flex-col gap-4">

            {/* ── Input card ── */}
            <div className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-md p-6 card-hover">
              <div className="grid md:grid-cols-2 gap-4 mb-4">

                {/* Upload CV */}
                <label className={`
                  cursor-pointer flex flex-col items-center justify-center gap-2 p-6
                  border-2 border-dashed rounded-2xl transition-all
                  ${cvLoaded
                    ? "border-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 dark:border-emerald-600"
                    : "border-gray-200 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 bg-gray-50 dark:bg-gray-800/50"
                  }
                `}>
                  <input type="file" accept=".pdf,.docx" className="hidden" onChange={handleCVUpload} />
                  {cvLoaded ? (
                    <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 border border-emerald-200 dark:border-emerald-700 flex items-center justify-center flex-shrink-0">
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M4 10.5l4.5 4.5 7.5-8" stroke="#10B981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </div>
                  ) : (
                    <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700/50 flex items-center justify-center flex-shrink-0">
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <rect x="4" y="2" width="9" height="16" rx="1.5" stroke="#2563EB" strokeWidth="1.5" />
                        <path d="M13 2l3 3v13a1.5 1.5 0 01-1.5 1.5H4.5A1.5 1.5 0 013 18V3.5A1.5 1.5 0 014.5 2" stroke="#2563EB" strokeWidth="1.5" strokeLinecap="round" />
                        <path d="M13 2v3h3" stroke="#2563EB" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M6.5 9h7M6.5 12h5" stroke="#2563EB" strokeWidth="1.5" strokeLinecap="round" />
                      </svg>
                    </div>
                  )}
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-200 text-center">
                    {cvLoaded ? cvFile?.name : "Upload your resume"}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500">PDF or DOCX · up to 5 MB</p>
                </label>

                {/* Textarea */}
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider ml-1">
                    Job description
                  </label>
                  <textarea
                    placeholder="Paste the job description here..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="flex-1 min-h-[140px] p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-600 rounded-2xl text-sm text-gray-700 dark:text-gray-200 placeholder:text-gray-400 dark:placeholder:text-gray-600 resize-none outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all"
                  />
                </div>
              </div>

              <button
                onClick={handleMatch}
                disabled={loading || !cvLoaded}
                className="w-full py-4 btn-primary disabled:bg-gray-200 dark:disabled:bg-gray-700 disabled:text-gray-400 disabled:shadow-none disabled:cursor-not-allowed rounded-2xl text-sm flex items-center justify-center gap-2"
              >
                {loading ? (
                  <span className="spinner" />
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 18 18" fill="none">
                      <path d="M9 2v10M5 6l4-4 4 4M3 14h12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    Analyze Compatibility
                  </>
                )}
              </button>

              {error && (
                <div className="mt-3 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-xl text-sm text-red-600 dark:text-red-400">
                  {error}
                </div>
              )}
            </div>

            {/* ── Results ── */}
            {matchScore !== null && (
              <>

                {/* ── 1 & 2. SCORE OVERVIEW — 2 cards | círculo | 2 cards ── */}
                <div className="">
                  <div className="flex items-center gap-4">

                    {/* Izquierda — 2 stat cards apiladas */}
                    <div className="flex flex-col gap-3 flex-shrink-0 w-36">
                      <StatCard label="Overall" value={overallSimilarity ?? 0} sublabel="Semantic match" />
                      <StatCard label="Skills" value={sectionSimilarities.skills_semantic ?? 0} sublabel="Skill alignment" />
                    </div>

                    {/* Centro — círculo grande */}
                    <div className="flex-1 flex flex-col items-center gap-3">
                      <div className="relative w-36 h-36 flex items-center justify-center">
                        <svg width="144" height="144" viewBox="0 0 64 64">
                          <circle cx="32" cy="32" r="26" fill="none" stroke="#E5E7EB" strokeWidth="4" className="dark:stroke-gray-700" />
                          <circle
                            cx="32" cy="32" r="26" fill="none"
                            stroke={getCircleStroke(matchScore)} strokeWidth="4"
                            strokeDasharray={circumference}
                            strokeDashoffset={dashOffset}
                            strokeLinecap="round"
                            transform="rotate(-90 32 32)"
                            style={{ transition: "stroke-dashoffset 0.8s ease" }}
                          />
                        </svg>
                        <div className="absolute flex flex-col items-center">
                          <span className="text-3xl font-extrabold text-gray-800 dark:text-gray-100 leading-none">
                            {matchScore}%
                          </span>
                          <span className="text-xs text-gray-400 dark:text-gray-500 mt-1">match score</span>
                        </div>
                      </div>

                      {matchRating && (
                        <span className={`text-sm font-bold uppercase tracking-widest px-5 py-2 rounded-full border ${getRatingClasses(matchScore)}`}>
                          {matchRating}
                        </span>
                      )}

                      {recommendation && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 text-center max-w-[180px] leading-relaxed">
                          {recommendation}
                        </p>
                      )}

                      {isFallback && (
                        <div className="px-3 py-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700/50 rounded-xl text-xs text-amber-700 dark:text-amber-400 text-center">
                          Limited analysis — section breakdown unavailable
                        </div>
                      )}
                    </div>

                    {/* Derecha — 2 stat cards apiladas */}
                    <div className="flex flex-col gap-3 flex-shrink-0 w-36">
                      <StatCard label="Experience" value={sectionSimilarities.experience ?? 0} sublabel="Relevance" />
                      <StatCard label="Keywords" value={tfidfSimilarity ?? 0} sublabel="TF-IDF match" />
                    </div>

                  </div>
                </div>

                {/* ── 3. SUMMARIES — 2 columns ── */}
                <div className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-md p-6 card-hover">
                  <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-4">
                    Summaries
                  </p>
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Job summary */}
                    <div>
                      <p className="text-xs font-semibold text-blue-500 dark:text-blue-400 uppercase tracking-wide mb-2">
                        Job summary
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                        {jobSummary || <span className="italic text-gray-400">No summary available.</span>}
                      </p>
                    </div>
                    {/* Candidate summary */}
                    <div>
                      <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-500 uppercase tracking-wide mb-2">
                        Candidate summary
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                        {cvSummary || <span className="italic text-gray-400">No summary available.</span>}
                      </p>
                    </div>
                  </div>
                </div>

                {/* ── 4. JOB REQUIREMENTS + KEY PHRASES — 2 columns ── */}
                <div className="grid md:grid-cols-2 gap-4">

                  {/* Job requirements */}
                  <div className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-md p-6 card-hover">
                    <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-4">
                      Job requirements
                    </p>

                    {requiredSkills.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">Required skills</p>
                        <div className="flex flex-wrap gap-1.5">
                          {requiredSkills.map((s) => (
                            <span key={s} className="px-2.5 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs font-medium rounded-full border border-gray-200 dark:border-gray-600">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {preferredSkills.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">Preferred skills</p>
                        <div className="flex flex-wrap gap-1.5">
                          {preferredSkills.map((s) => (
                            <span key={s} className="px-2.5 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs font-medium rounded-full border border-blue-200 dark:border-blue-700/50">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {(experienceYears || educationLevel) && (
                      <div className="border-t border-gray-100 dark:border-gray-700 pt-4 grid grid-cols-2 gap-3">
                        {experienceYears && (
                          <div>
                            <p className="text-xs text-gray-400 dark:text-gray-500 mb-0.5">Experience</p>
                            <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">{experienceYears}</p>
                          </div>
                        )}
                        {educationLevel && (
                          <div>
                            <p className="text-xs text-gray-400 dark:text-gray-500 mb-0.5">Education</p>
                            <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">{educationLevel}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Key phrases */}
                  <div className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-md p-6 card-hover">
                    <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-4">
                      Key phrases
                    </p>
                    {keyPhrases.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {keyPhrases.map((phrase) => (
                          <span key={phrase} className="px-2.5 py-1 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 text-xs font-medium rounded-full border border-purple-200 dark:border-purple-700/50">
                            {phrase}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm italic text-gray-400 dark:text-gray-500">No key phrases detected.</p>
                    )}
                  </div>
                </div>

                {/* ── 5. SKILL ANALYSIS — 1 full column ── */}
                {skillDetails && !isFallback && (
                  <div className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-md p-6 card-hover">
                    <div className="flex items-center justify-between mb-5">
                      <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                        Skill analysis
                      </p>
                      <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                        {skillDetails.matched_count}/{skillDetails.job_skills_count} matched
                      </span>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                      {skillDetails.matched_skills.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-500 uppercase tracking-wide mb-2">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center flex-shrink-0">
                                <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                                  <path d="M2 5.5l2.5 2.5 4.5-4.5" stroke="#10B981" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                                    <animate attributeName="stroke-dasharray" from="0 20" to="20 20" dur="0.4s" fill="freeze" />
                                  </path>
                                </svg>
                              </div>
                              <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-500 uppercase tracking-wide">
                                Matched skills
                              </p>
                            </div>
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {skillDetails.matched_skills.map((skill) => (
                              <span key={skill} className="px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-medium rounded-full border border-emerald-200 dark:border-emerald-700/50">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {skillDetails.missing_skills.length > 0 && (
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-5 h-5 rounded-full bg-red-100 dark:bg-red-900/40 flex items-center justify-center flex-shrink-0">
                              <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                                <path d="M2.5 2.5l6 6M8.5 2.5l-6 6" stroke="#EF4444" strokeWidth="1.8" strokeLinecap="round">
                                  <animate attributeName="stroke-dasharray" from="0 20" to="20 20" dur="0.4s" fill="freeze" />
                                </path>
                              </svg>
                            </div>
                            <p className="text-xs font-semibold text-red-500 dark:text-red-400 uppercase tracking-wide">
                              Missing skills
                            </p>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {skillDetails.missing_skills.map((skill) => (
                              <span key={skill} className="px-2.5 py-1 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-xs font-medium rounded-full border border-red-200 dark:border-red-700/50">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {skillDetails.extra_skills?.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-5 h-5 rounded-full bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center flex-shrink-0">
                            <svg width="11" height="11" viewBox="0 0 11 11">
                              <path
                                d="M5.5 1l1.2 2.6 2.8.4-2 2 .5 2.8-2.5-1.4L3 8.8l.5-2.8-2-2 2.8-.4z"
                                fill="#2563EB"
                                stroke="#2563EB"
                                strokeWidth="0.5"
                                strokeLinejoin="round"
                              >
                                <animate attributeName="opacity" from="0" to="1" dur="0.4s" fill="freeze" />
                                <animateTransform attributeName="transform" type="scale" from="0 0" to="1 1" dur="0.4s" additive="sum" fill="freeze" calcMode="spline" keySplines="0.34 1.56 0.64 1" />
                              </path>
                            </svg>
                          </div>
                          <p className="text-xs font-semibold text-blue-500 dark:text-blue-400 uppercase tracking-wide">
                            Extra skills
                          </p>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {skillDetails.extra_skills.map((skill) => (
                            <span key={skill} className="px-2.5 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs font-medium rounded-full border border-blue-200 dark:border-blue-700/50">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* ── 6. STRENGTHS & GAPS ── */}
                {(strengths.length > 0 || gaps.length > 0) && (
                  <div className="grid md:grid-cols-2 gap-4">
                    {strengths.length > 0 && (
                      <div className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-md p-6 card-hover">
                        <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-500 uppercase tracking-wider mb-4">
                          Strengths
                        </p>
                        <ul className="space-y-2.5">
                          {strengths.map((item, i) => (
                            <li key={i} className="flex items-start gap-2.5 text-sm text-gray-600 dark:text-gray-300">
                              <span className="mt-0.5 w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xs font-bold flex-shrink-0">
                                +
                              </span>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {gaps.length > 0 && (
                      <div className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-md p-6 card-hover">
                        <p className="text-xs font-semibold text-orange-500 dark:text-orange-400 uppercase tracking-wider mb-4">
                          Gaps
                        </p>
                        <ul className="space-y-2.5">
                          {gaps.map((item, i) => (
                            <li key={i} className="flex items-start gap-2.5 text-sm text-gray-600 dark:text-gray-300">
                              <span className="mt-0.5 w-5 h-5 rounded-full bg-orange-100 dark:bg-orange-900/40 text-orange-600 dark:text-orange-400 flex items-center justify-center text-xs font-bold flex-shrink-0">
                                –
                              </span>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

              </>
            )}
          </div>
        </main>

        <Footer />
      </div>
    </Paywall>
  );
}