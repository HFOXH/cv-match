"use client";

import { useState, useRef, ChangeEvent } from "react";
import Navbar from "@/components/Navbar";
import Paywall from "@/components/Paywall";
import Footer from "@/components/Footer";

// Backend pipeline stages, in the order routes/match.py runs them.
// `est` is the typical duration in ms (used to animate the highlight while
// the backend is working — the backend doesn't stream progress, so we
// estimate). `key` matches the field in the response's `timing` object.
const PIPELINE_STEPS = [
  { key: "cv_processing",    label: "Extract & parse CV",    desc: "Read PDF/DOCX, GPT-4o-mini parses structure",       est: 10000 },
  { key: "cv_normalization", label: "Normalize CV",          desc: "GPT reformats CV into comparison-ready fields",     est: 6000  },
  { key: "jd_preprocessing", label: "Preprocess JD",         desc: "GPT extracts skills, requirements, key phrases",    est: 5000  },
  { key: "cv_encoding",      label: "Embed CV sections",     desc: "OpenAI embeddings for skills / experience / overall", est: 1500 },
  { key: "jd_encoding",      label: "Embed JD sections",     desc: "OpenAI embeddings for the job description",        est: 1500  },
  { key: "scoring",          label: "Match & score",         desc: "Jaccard + fuzzy + semantic matching, sigmoid calibration", est: 5000 },
];

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
  const [rawScores, setRawScores] = useState<Record<string, number>>({});
  const [isFallback, setIsFallback] = useState(false);
  const [jdParseFailed, setJdParseFailed] = useState(false);
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

  // Pipeline progress state. currentStepIdx: -1 = never run, 0..5 = currently
  // running that step, >=6 = all steps done. timing is the real breakdown
  // from the backend response once it arrives.
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(-1);
  const [timing, setTiming] = useState<Record<string, number> | null>(null);
  const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const analyzeStartRef = useRef<number>(0);

  const circumference = 2 * Math.PI * 48;
  const scoreColor = (n: number) => n >= 70 ? "#10b981" : n >= 40 ? "#f59e0b" : "#ef4444";
  const barColor = (n: number) => n >= 70 ? "bg-emerald-500" : n >= 40 ? "bg-amber-500" : "bg-red-500";
  const tagStyle = (n: number) =>
    n >= 70 ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
      : n >= 40 ? "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
        : "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400";

  const handleCVUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) { setCvFile(file); setCvLoaded(true); }
  };

  const handleMatch = async () => {
    if (!cvLoaded || !text.trim()) return;
    setLoading(true);
    setError("");

    // Start the pipeline progress animation. The backend doesn't stream
    // progress, so we advance the highlighted step based on cumulative
    // estimated durations. When the real response arrives, we replace
    // the estimates with real timings in the `timing` state.
    setTiming(null);
    setCurrentStepIdx(0);
    analyzeStartRef.current = Date.now();
    if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    progressIntervalRef.current = setInterval(() => {
      const elapsed = Date.now() - analyzeStartRef.current;
      let cum = 0;
      let idx = PIPELINE_STEPS.length - 1;
      for (let i = 0; i < PIPELINE_STEPS.length; i++) {
        cum += PIPELINE_STEPS[i].est;
        if (elapsed < cum) { idx = i; break; }
      }
      setCurrentStepIdx(idx);
    }, 200);

    let succeeded = false;
    try {
      const formData = new FormData();
      formData.append("file", cvFile!);
      formData.append("job_description", text);
      const response = await fetch("http://localhost:8000/api/v1/match", { method: "POST", body: formData });
      if (!response.ok) {
        const err = await response.json().catch(() => null);
        setError(err?.detail || "An error occurred while analyzing. Please try again.");
        setMatchScore(null);
        return;
      }
      const r = await response.json();
      console.log("[match] backend response:", r);
      setMatchScore(r.match_score);
      setCvSummary(r.cv_summary);
      setJobSummary(r.job_summary);
      setRequiredSkills(r.required_skills || []);
      setPreferredSkills(r.preferred_skills || []);
      setExperienceYears(r.experience_years);
      setEducationLevel(r.education_level);
      setKeyPhrases(r.key_phrases || []);
      setOverallSimilarity(r.overall_similarity);
      setSectionSimilarities(r.section_similarities || {});
      setRawScores(r.raw_scores || {});
      setIsFallback(r.is_fallback || false);
      setJdParseFailed(r.jd_parse_failed || false);
      setMatchRating(r.match_rating || "");
      setRecommendation(r.recommendation || "");
      setSkillDetails(r.skill_details || null);
      setStrengths(r.strengths || []);
      setGaps(r.gaps || []);
      setTiming(r.timing || null);
      succeeded = true;
    } catch {
      setError("Could not connect to the server. Please make sure the backend is running.");
      setMatchScore(null);
    } finally {
      setLoading(false);
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      // On success, mark all pipeline steps as done. On any error
      // (HTTP failure or network error), reset the pipeline to idle so
      // the user sees a clean slate when they retry.
      setCurrentStepIdx(succeeded ? PIPELINE_STEPS.length : -1);
    }
  };

  const scoreOffset = matchScore !== null
    ? circumference - (matchScore / 100) * circumference
    : circumference;

  // Take the stronger signal: the skills-match score (keyword + fuzzy + semantic
  // reconciliation, from section_similarities.skills_match) vs the raw semantic
  // cosine % (from raw_scores.skills_semantic). This way the display reflects
  // semantic alignment when exact/fuzzy keyword matching misses synonyms —
  // e.g., "retail customer service" vs "customer service".
  const skillsMatchValue = Math.round(
    Math.max(
      sectionSimilarities.skills_match ?? sectionSimilarities.skills_semantic ?? 0,
      (rawScores.skills_semantic ?? 0) * 100,
    )
  );

  const bars = [
    { label: "Overall semantic", value: overallSimilarity ?? 0, show: true },
    { label: "Skills similarity", value: skillsMatchValue, show: !isFallback },
    { label: "Experience relevance", value: sectionSimilarities.experience ?? 0, show: !isFallback },
    { label: "Education alignment", value: sectionSimilarities.education ?? 0, show: !isFallback },
  ].filter((b) => b.show);

  return (
    <Paywall>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 antialiased">
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');
          html, body, * { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }
          .font-mono-dm { font-family: 'DM Mono', monospace; }

          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
          }
          .fade-up { animation: fadeUp 0.45s ease-out forwards; }
          .upload-zone { transition: background 0.15s, border-color 0.15s, transform 0.15s; }
          .upload-zone:hover { transform: translateY(-1px); }
          .bar-fill { transition: width 0.9s cubic-bezier(.4,0,.2,1); }
          .arc-path { transition: stroke-dashoffset 1s cubic-bezier(.4,0,.2,1), stroke 0.4s; }

          .btn-primary {
            background: #2563EB;
            color: #fff;
            font-weight: 600;
            transition: background 0.18s, transform 0.14s, box-shadow 0.18s;
            box-shadow: 0 2px 0 #1D4ED8;
          }
          .btn-primary:hover:not(:disabled) { background: #1D4ED8; transform: translateY(-1px); box-shadow: 0 4px 0 #1E40AF; }
          .btn-primary:active:not(:disabled) { transform: translateY(1px); box-shadow: 0 1px 0 #1E40AF; }
        `}</style>

        <Navbar />

        <main className="max-w-4xl mx-auto px-6 pb-24">

          {/* Hero — score donut right side */}
          <header className="flex items-start justify-between gap-6 my-12 pb-8 border-b border-gray-200 dark:border-gray-700">
            <div>
              <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-widest text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800/50 px-3 py-1 rounded-full mb-3">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block" />
                AI-Powered Analysis
              </span>
              <h1 className="text-3xl font-semibold tracking-tight text-gray-900 dark:text-white mb-1.5">
                Resume Matcher
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                Upload your CV and compare it with any<br className="hidden sm:block" /> job description instantly.
              </p>
            </div>

            {/* Score donut */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="relative w-[108px] h-[108px]">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 110 110">
                  <circle cx="55" cy="55" r="48" fill="none" stroke="currentColor"
                    className="text-gray-200 dark:text-gray-700" strokeWidth="5" />
                  <circle cx="55" cy="55" r="48" fill="none"
                    stroke={matchScore !== null ? scoreColor(matchScore) : "#d1d5db"}
                    strokeWidth="5" strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={scoreOffset}
                    className="arc-path" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-mono-dm text-2xl font-semibold text-gray-900 dark:text-white leading-none">
                    {matchScore !== null ? `${matchScore}%` : "—"}
                  </span>
                  <span className="text-[10px] font-medium uppercase tracking-wider text-gray-400 dark:text-gray-500 mt-0.5">match</span>
                </div>
              </div>
              {matchRating && matchScore !== null && (
                <span className={`mt-2.5 text-[11px] font-semibold uppercase tracking-wide px-3 py-1 rounded-full ${tagStyle(matchScore)}`}>
                  {matchRating}
                </span>
              )}
            </div>
          </header>

          {/* Input */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <label className={`upload-zone cursor-pointer flex flex-col items-center justify-center gap-2 p-8 rounded-2xl border-2 border-dashed min-h-[120px]
              ${cvLoaded
                ? "border-emerald-300 dark:border-emerald-700 bg-emerald-50 dark:bg-emerald-900/20"
                : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-blue-300"}`}>
              <input type="file" accept=".pdf,.docx" className="hidden" onChange={handleCVUpload} />
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${cvLoaded ? "bg-emerald-100 dark:bg-emerald-900/40" : "bg-blue-50 dark:bg-blue-900/30"}`}>
                {cvLoaded
                  ? <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M4 9.5l3.5 3.5 6-7" stroke="#10b981" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  : <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 3v9M5 6l4-3 4 3M3 14h12" stroke="#3b82f6" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
                }
              </div>
              <div className="text-center">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                  {cvLoaded ? (cvFile!.name.length > 26 ? cvFile!.name.slice(0, 26) + "…" : cvFile!.name) : "Upload your resume"}
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">PDF or DOCX — max 5MB</p>
              </div>
            </label>

            <textarea
              placeholder="Paste here the job description..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl focus:ring-2 focus:ring-blue-400/30 focus:outline-none min-h-[120px] resize-none text-sm text-gray-700 dark:text-gray-200 placeholder-gray-400 transition-all"
            />
          </div>

          <button
            onClick={handleMatch}
            disabled={loading || !cvLoaded}
            className="cursor-pointer w-full py-4 btn-primary disabled:bg-gray-200 dark:disabled:bg-gray-700 disabled:text-gray-400 disabled:shadow-none disabled:cursor-not-allowed rounded-2xl text-sm flex items-center justify-center gap-2 mb-4"
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
            <div className="mb-4 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-xl text-sm text-red-700 dark:text-red-400">{error}</div>
          )}

          {/* How it works — live pipeline visualization */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 mb-6">
            <div className="flex items-start justify-between gap-3 mb-5">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">How it works</p>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                  {currentStepIdx === -1 && "Six stages run each time you analyze. Click above to watch them light up."}
                  {currentStepIdx >= 0 && currentStepIdx < PIPELINE_STEPS.length && "Analyzing… each stage is lighting up as it runs."}
                  {currentStepIdx >= PIPELINE_STEPS.length && "All stages complete. Real timings shown on the right."}
                </p>
              </div>
              {timing && typeof timing.total_ms === "number" && (
                <span className="text-[11px] font-mono-dm text-gray-400 dark:text-gray-500 whitespace-nowrap flex-shrink-0 mt-1">
                  total {(timing.total_ms / 1000).toFixed(1)}s
                </span>
              )}
            </div>

            <ol className="space-y-3">
              {PIPELINE_STEPS.map((step, i) => {
                const isActive = loading && i === currentStepIdx;
                const isDone = currentStepIdx >= PIPELINE_STEPS.length || (currentStepIdx >= 0 && i < currentStepIdx);
                const isIdle = currentStepIdx === -1;
                const isPending = !isActive && !isDone && !isIdle;
                const realMs = timing?.[`${step.key}_ms`];

                const circleClass =
                  isActive ? "bg-blue-500 text-white ring-4 ring-blue-200 dark:ring-blue-900/50 animate-pulse"
                  : isDone  ? "bg-emerald-500 text-white"
                  :           "bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500";

                const titleClass =
                  isActive ? "text-blue-600 dark:text-blue-400 font-semibold"
                  : isDone  ? "text-gray-800 dark:text-gray-100 font-medium"
                  : isPending ? "text-gray-400 dark:text-gray-500 font-medium"
                  :           "text-gray-700 dark:text-gray-200 font-medium";

                return (
                  <li key={step.key} className="flex items-start gap-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all ${circleClass}`}>
                      {isDone
                        ? <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7.5l2.5 2.5 5.5-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                        : i + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline justify-between gap-2">
                        <p className={`text-sm transition-colors ${titleClass}`}>{step.label}</p>
                        {typeof realMs === "number" && (
                          <span className="text-[11px] font-mono-dm text-gray-400 dark:text-gray-500 flex-shrink-0">
                            {(realMs / 1000).toFixed(1)}s
                          </span>
                        )}
                      </div>
                      <p className={`text-xs mt-0.5 leading-relaxed transition-colors ${isActive || isDone ? "text-gray-500 dark:text-gray-400" : "text-gray-400 dark:text-gray-500"}`}>
                        {step.desc}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ol>
          </div>

          {/* Results */}
          {matchScore !== null && (
            <div className="space-y-6 fade-up">

              {/* 4 metric cards */}
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-3">Score breakdown</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { label: "Overall", value: overallSimilarity ?? 0, sub: "semantic", show: true },
                    { label: "Skills", value: skillsMatchValue, sub: "similarity", show: !isFallback },
                    { label: "Experience", value: sectionSimilarities.experience ?? 0, sub: "relevance", show: !isFallback },
                    { label: "Education", value: sectionSimilarities.education ?? 0, sub: "alignment", show: !isFallback },
                  ].filter((m) => m.show).map((m) => (
                    <div key={m.label} className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4">
                      <p className="text-[11px] text-gray-500 dark:text-gray-400 font-medium mb-1">{m.label}</p>
                      <p className="font-mono-dm text-2xl font-semibold text-gray-900 dark:text-white leading-none">{m.value}%</p>
                      <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-1">{m.sub}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Progress bars */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6">
                {isFallback && (
                  <div className="mb-4 text-xs text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-lg px-3 py-2">
                    Limited analysis — section breakdown unavailable
                  </div>
                )}
                {jdParseFailed && (
                  <div className="mb-4 text-xs text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-lg px-3 py-2">
                    Job description could not be parsed — skills and requirements may be missing. Try resubmitting.
                  </div>
                )}
                <div className="space-y-4">
                  {bars.map((b) => (
                    <div key={b.label}>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-gray-600 dark:text-gray-300 font-medium">{b.label}</span>
                        <span className="font-mono-dm text-gray-500 dark:text-gray-400">{b.value}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full bar-fill ${barColor(b.value)}`} style={{ width: `${Math.min(b.value, 100)}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendation */}
              {recommendation && (
                <div className="flex items-center gap-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/50 rounded-2xl px-5 py-4">
                  <div className="w-9 h-9 bg-blue-100 dark:bg-blue-900/40 rounded-xl flex items-center justify-center flex-shrink-0">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <circle cx="8" cy="8" r="6" stroke="#3b82f6" strokeWidth="1.5" />
                      <path d="M8 5v3l2 2" stroke="#3b82f6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <p className="text-sm text-blue-800 dark:text-blue-300">
                    <span className="font-semibold">Recommendation: </span>{recommendation}
                  </p>
                </div>
              )}

              {/* Summaries */}
              <div className="grid md:grid-cols-2 gap-4">
                {[{ title: "Job summary", body: jobSummary }, { title: "Candidate summary", body: cvSummary }].map((s) => (
                  <div key={s.title} className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5">
                    <p className="text-[11px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-3">{s.title}</p>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{s.body || "—"}</p>
                  </div>
                ))}
              </div>

              {/* Requirements + Key phrases */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5">
                  <p className="text-[11px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-3">Job requirements</p>
                  <div className="divide-y divide-gray-100 dark:divide-gray-700">
                    {[
                      { key: "Required skills", val: requiredSkills.slice(0, 4).join(", ") + (requiredSkills.length > 4 ? "…" : "") },
                      { key: "Preferred skills", val: preferredSkills.slice(0, 3).join(", ") + (preferredSkills.length > 3 ? "…" : "") },
                      { key: "Experience", val: experienceYears },
                      { key: "Education", val: educationLevel },
                    ].filter((r) => r.val).map((r) => (
                      <div key={r.key} className="flex justify-between items-baseline py-2 text-sm">
                        <span className="text-gray-500 dark:text-gray-400">{r.key}</span>
                        <span className="font-medium text-gray-800 dark:text-gray-200 text-xs text-right max-w-[55%]">{r.val}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5">
                  <p className="text-[11px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-3">Key phrases</p>
                  <div className="flex flex-wrap gap-1.5">
                    {keyPhrases.slice(0, 12).map((p) => (
                      <span key={p} className="text-[11px] font-medium px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600">{p}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Skills */}
              {skillDetails && !isFallback && (
                <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 space-y-5">
                  <div className="flex items-center justify-between">
                    <p className="text-[11px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">Skill analysis</p>
                    <span className="text-xs font-semibold text-gray-400">{skillDetails.matched_count}/{skillDetails.job_skills_count} matched</span>
                  </div>
                  {[
                    { label: "Matched", color: "text-emerald-600 dark:text-emerald-500", chipClass: "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50", skills: skillDetails.matched_skills },
                    { label: "Missing", color: "text-red-500 dark:text-red-400", chipClass: "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800/50", skills: skillDetails.missing_skills },
                    { label: "Additional", color: "text-gray-400 dark:text-gray-500", chipClass: "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600", skills: skillDetails.extra_skills || [] },
                  ].filter((g) => g.skills.length > 0).map((g) => (
                    <div key={g.label}>
                      <p className={`text-[11px] font-semibold uppercase tracking-widest mb-2 ${g.color}`}>{g.label}</p>
                      <div className="flex flex-wrap gap-1.5">
                        {g.skills.map((s) => <span key={s} className={`text-[11px] font-medium px-2.5 py-1 rounded-full ${g.chipClass}`}>{s}</span>)}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Strengths & Gaps */}
              {(strengths.length > 0 || gaps.length > 0) && (
                <div className="grid md:grid-cols-2 gap-4">
                  {strengths.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5">
                      <p className="text-[11px] font-semibold uppercase tracking-widest text-emerald-600 dark:text-emerald-500 mb-3">Strengths</p>
                      <ul className="space-y-2">
                        {strengths.map((item, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0 mt-1.5" />{item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {gaps.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5">
                      <p className="text-[11px] font-semibold uppercase tracking-widest text-amber-500 dark:text-amber-400 mb-3">Gaps</p>
                      <ul className="space-y-2">
                        {gaps.map((item, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 flex-shrink-0 mt-1.5" />{item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </main>
        <Footer />
      </div>
    </Paywall>
  );
}