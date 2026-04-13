"use client";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const WEIGHTS = [
  { label: "Overall semantic", value: 30, color: "bg-blue-500", desc: "How close your full CV is in meaning to the full job description." },
  { label: "Skills keyword match", value: 25, color: "bg-emerald-500", desc: "How many of the job's required skills appear in your CV (exact + fuzzy)." },
  { label: "Experience match", value: 25, color: "bg-amber-500", desc: "Whether your past job titles and responsibilities line up with what the role asks for." },
  { label: "Skills semantic match", value: 10, color: "bg-indigo-500", desc: "Catch-up signal for skills that didn't match by keyword but are semantically equivalent." },
  { label: "Education match", value: 10, color: "bg-violet-500", desc: "Whether your degree level meets or exceeds the job's requirement." },
];

const PIPELINE = [
  { label: "Extract & parse CV", desc: "We read your PDF/DOCX and use GPT-4o-mini to pull out skills, experience, and education into structured fields." },
  { label: "Normalize CV", desc: "A second GPT pass cleans up abbreviations (JS → JavaScript, CPR → cardiopulmonary resuscitation) and dedupes skills." },
  { label: "Preprocess JD", desc: "We extract required vs preferred skills, experience/education requirements, and a summary from the job posting." },
  { label: "Embed sections", desc: "Each section (skills, experience, education, overall) gets converted to a 1536-dim vector using text-embedding-3-small." },
  { label: "Match & score", desc: "Jaccard + fuzzy skill match, cosine similarity between section vectors, education/experience boosts, then sigmoid calibration." },
];

const BANDS = [
  { range: "90–100%", label: "Excellent Match", rec: "Strong candidate — definitely apply", color: "bg-emerald-500" },
  { range: "75–90%", label: "Good Match", rec: "Good candidate — apply with confidence", color: "bg-lime-500" },
  { range: "60–75%", label: "Moderate Match", rec: "Consider applying — highlight transferable skills", color: "bg-amber-500" },
  { range: "40–60%", label: "Weak Match", rec: "Significant gaps — apply cautiously", color: "bg-orange-500" },
  { range: "0–40%", label: "Poor Match", rec: "Not recommended — major misalignment", color: "bg-red-500" },
];

export default function ScoringPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 antialiased">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
        body { font-family: 'DM Sans', sans-serif; }
        .font-mono-dm { font-family: 'DM Mono', monospace; }
      `}</style>

      <Navbar />

      <main className="max-w-4xl mx-auto px-6 py-16">
        {/* Hero */}
        <div className="mb-16 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 mb-5">
            <span className="text-xs font-semibold text-blue-600 dark:text-blue-400 tracking-wider uppercase">How it works</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
            How we score your <span className="text-blue-600 dark:text-blue-400">match</span>
          </h1>
          <p className="text-gray-500 dark:text-gray-400 text-lg max-w-2xl mx-auto">
            A breakdown of what happens between clicking &ldquo;Analyze&rdquo; and seeing your percentage.
            Plain-language first, with the technical details underneath.
          </p>
        </div>

        {/* Pipeline */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">The pipeline</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Every analysis runs through five stages. If any stage can&rsquo;t produce meaningful signal,
            we refuse to score rather than show you a misleading number.
          </p>
          <ol className="space-y-3">
            {PIPELINE.map((step, i) => (
              <li key={step.label} className="flex gap-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-semibold">
                  {i + 1}
                </div>
                <div>
                  <p className="font-semibold text-gray-800 dark:text-gray-100">{step.label}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mt-1">{step.desc}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        {/* Weights */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">What the score is made of</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Your final percentage is a weighted blend of five signals. Skills and overall
            semantic similarity carry the most weight because they matter the most.
          </p>
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 space-y-5">
            {WEIGHTS.map((w) => (
              <div key={w.label}>
                <div className="flex justify-between items-baseline mb-1.5">
                  <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{w.label}</span>
                  <span className="font-mono-dm text-sm text-gray-500 dark:text-gray-400">{w.value}%</span>
                </div>
                <div className="w-full h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden mb-1.5">
                  <div className={`h-full ${w.color} rounded-full`} style={{ width: `${w.value * 2.5}%` }} />
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">{w.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 px-4 py-3 bg-gray-100 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg text-xs text-gray-500 dark:text-gray-400 font-mono-dm leading-relaxed">
            Technical: weighted_sum = 0.30·sbert_overall + 0.25·skills_jaccard + 0.25·experience_match + 0.10·skills_semantic + 0.10·education_match
          </div>
        </section>

        {/* Skill matching */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">How skills are matched</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            A skill isn&rsquo;t just a string match. We try three increasingly smart strategies
            so synonyms and variants don&rsquo;t get missed.
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { n: "01", title: "Exact", plain: "Does the CV literally list the same skill the job asks for?", tech: "set intersection on lowercased skills" },
              { n: "02", title: "Fuzzy", plain: "Close enough — catches typos, plurals, and partial word matches.", tech: "SequenceMatcher ratio ≥ 0.8 or word-boundary substring" },
              { n: "03", title: "Semantic", plain: "Different words, same meaning. GPT-4o-mini reconciles leftovers.", tech: "GPT-4o-mini pairs remaining CV ↔ JD skills with temperature 0" },
            ].map((s) => (
              <div key={s.n} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
                <p className="text-[11px] font-black tracking-widest text-blue-600 dark:text-blue-400 mb-2">{s.n}</p>
                <p className="font-semibold text-gray-800 dark:text-gray-100 mb-2">{s.title}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-3">{s.plain}</p>
                <p className="text-[11px] text-gray-400 dark:text-gray-500 font-mono-dm leading-relaxed">{s.tech}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Boosts */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">Education &amp; experience boosts</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Semantic similarity alone doesn&rsquo;t tell the whole story — a PhD candidate
            with no exact skill match can still be right for a research role. We layer
            in explicit checks on top of the cosine similarity.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
              <p className="font-semibold text-gray-800 dark:text-gray-100 mb-2">Education ladder</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-3">
                PhD → Master&rsquo;s → Bachelor&rsquo;s → Diploma → High School. If your level
                meets or exceeds the job requirement, the score is boosted to at least 0.8.
                One level below gets partial credit (0.5).
              </p>
              <p className="text-[11px] text-gray-400 dark:text-gray-500 font-mono-dm">
                max(semantic_sim, 0.8) if cv_level ≥ jd_level<br />
                max(semantic_sim, 0.5) if cv_level == jd_level − 1
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
              <p className="font-semibold text-gray-800 dark:text-gray-100 mb-2">Job title overlap</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed mb-3">
                Direct substring match on your past titles boosts experience to 0.85.
                Shared key words (like &ldquo;data scientist&rdquo;) give partial credit
                even when the rest of the phrasing differs.
              </p>
              <p className="text-[11px] text-gray-400 dark:text-gray-500 font-mono-dm">
                substring hit → 0.85<br />
                word overlap ≥ 50% → 0.75<br />
                word overlap ≥ 25% → 0.60
              </p>
            </div>
          </div>
        </section>

        {/* Calibration */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">Why 0.30 raw becomes 50%</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Raw similarity scores cluster in the 0.3–0.8 range — a cosine of 0.45 between
            two CV/JD pairs is actually a respectable match, but shown as 45% it looks bad.
            We pass the raw score through a sigmoid curve centered at 0.30 so the final
            percentage reads the way humans expect it to.
          </p>
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
            <p className="text-[11px] text-gray-400 dark:text-gray-500 font-mono-dm mb-3">
              calibrated = 1 / (1 + exp(−8 · (raw_score − 0.30)))
            </p>
            <div className="grid grid-cols-5 gap-2 text-center">
              {[
                { raw: "0.10", pct: "15%" },
                { raw: "0.30", pct: "50%" },
                { raw: "0.50", pct: "83%" },
                { raw: "0.70", pct: "96%" },
                { raw: "0.90", pct: "99%" },
              ].map((r) => (
                <div key={r.raw} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-2">
                  <p className="text-[10px] text-gray-400 font-mono-dm">{r.raw}</p>
                  <p className="text-sm font-semibold text-gray-800 dark:text-gray-100">{r.pct}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Bands */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">What your percentage means</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            The final number maps to one of five recommendations.
          </p>
          <div className="space-y-2">
            {BANDS.map((b) => (
              <div key={b.label} className="flex items-center gap-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl">
                <div className={`flex-shrink-0 w-3 h-12 ${b.color} rounded-full`} />
                <div className="flex-shrink-0 w-20 font-mono-dm text-sm text-gray-500 dark:text-gray-400">{b.range}</div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-800 dark:text-gray-100">{b.label}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{b.rec}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <div className="text-center py-8">
          <a href="/analyzer" className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors">
            Try it on your CV →
          </a>
        </div>
      </main>

      <Footer />
    </div>
  );
}
