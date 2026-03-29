"use client";

import { useState, useEffect, useRef } from "react";

// ─── Hook: scroll reveal ───────────────────────────────────────────────────────
function useReveal(threshold = 0.12) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } },
      { threshold }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, visible };
}

// ─── Animated counter ─────────────────────────────────────────────────────────
function Counter({ to, suffix = "" }: { to: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  const { ref, visible } = useReveal();
  useEffect(() => {
    if (!visible) return;
    let cur = 0;
    const step = to / 60;
    const id = setInterval(() => {
      cur += step;
      if (cur >= to) { setVal(to); clearInterval(id); } else setVal(Math.floor(cur));
    }, 16);
    return () => clearInterval(id);
  }, [visible, to]);
  return <span ref={ref}>{val}{suffix}</span>;
}

// ─── FAQ Item ─────────────────────────────────────────────────────────────────
function FAQItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-gray-200 dark:border-gray-700 last:border-0">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex justify-between items-center py-5 text-left group"
      >
        <span className="font-semibold text-gray-800 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors text-[15px]">
          {q}
        </span>
        <span className={`ml-4 flex-shrink-0 w-7 h-7 rounded-full border flex items-center justify-center transition-all duration-300 text-sm
          ${open
            ? "rotate-45 bg-blue-600 border-blue-600 text-white"
            : "border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400"
          }`}>
          +
        </span>
      </button>
      <div className={`overflow-hidden transition-all duration-300 ${open ? "max-h-48 pb-5" : "max-h-0"}`}>
        <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{a}</p>
      </div>
    </div>
  );
}

// ─── Dark mode toggle ─────────────────────────────────────────────────────────
function ThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = saved === "dark" || (!saved && prefersDark);
    setDark(isDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);
  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };
  return (
    <button
      onClick={toggle}
      aria-label="Toggle dark mode"
      className="w-9 h-9 rounded-xl flex items-center justify-center bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
    >
      {dark ? (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.5"/>
          <path d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M3.05 3.05l1.06 1.06M11.89 11.89l1.06 1.06M11.89 3.05l-1.06 1.06M4.11 11.89 3.05 12.95" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M13.5 10A6 6 0 0 1 6 2.5a.5.5 0 0 0-.6-.6A6.5 6.5 0 1 0 14.1 10.6a.5.5 0 0 0-.6-.6z" fill="currentColor"/>
        </svg>
      )}
    </button>
  );
}

// ─── Main Landing Page ────────────────────────────────────────────────────────
export default function LandingPage() {
  const [billingAnnual, setBillingAnnual] = useState(false);

  const heroReveal    = useReveal(0.05);
  const howReveal     = useReveal(0.1);
  const benefitReveal = useReveal(0.1);
  const pricingReveal = useReveal(0.1);
  const faqReveal     = useReveal(0.1);

  return (
    <div className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 antialiased overflow-x-hidden transition-colors duration-300">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
        *, *::before, *::after { box-sizing: border-box; }
        html, body { font-family: 'Poppins', sans-serif; }

        .reveal {
          opacity: 0;
          transform: translateY(22px);
          transition: opacity 0.6s cubic-bezier(.4,0,.2,1), transform 0.6s cubic-bezier(.4,0,.2,1);
        }
        .reveal.visible { opacity: 1; transform: none; }
        .reveal-delay-1 { transition-delay: 0.1s; }
        .reveal-delay-2 { transition-delay: 0.2s; }
        .reveal-delay-3 { transition-delay: 0.3s; }
        .reveal-delay-4 { transition-delay: 0.4s; }
        .reveal-delay-5 { transition-delay: 0.5s; }

        .card-hover { transition: transform 0.22s ease, box-shadow 0.22s ease; }
        .card-hover:hover { transform: translateY(-3px); box-shadow: 0 14px 28px -8px rgba(37,99,235,0.13); }

        .marquee {
          display: flex;
          gap: 48px;
          animation: marquee 22s linear infinite;
          white-space: nowrap;
        }
        @keyframes marquee {
          from { transform: translateX(0); }
          to   { transform: translateX(-50%); }
        }

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
          font-family: 'Poppins', sans-serif;
          font-weight: 600;
          transition: background 0.18s, transform 0.14s, box-shadow 0.18s;
          box-shadow: 0 2px 0 #1D4ED8;
        }
        .btn-primary:hover  { background: #1D4ED8; transform: translateY(-1px); box-shadow: 0 4px 0 #1E40AF; }
        .btn-primary:active { transform: translateY(1px); box-shadow: 0 1px 0 #1E40AF; }

        .btn-outline {
          background: transparent;
          color: #2563EB;
          border: 2px solid #2563EB;
          font-family: 'Poppins', sans-serif;
          font-weight: 600;
          transition: background 0.18s, color 0.18s;
        }
        .btn-outline:hover { background: #EFF6FF; }
        .dark .btn-outline { color: #60A5FA; border-color: #60A5FA; }
        .dark .btn-outline:hover { background: #1E3A8A; }
      `}</style>

      {/* ── NAV ─────────────────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 bg-gray-50/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 transition-colors">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="2" width="5" height="5" rx="1" fill="white"/>
                <rect x="9" y="2" width="5" height="5" rx="1" fill="white" opacity="0.5"/>
                <rect x="2" y="9" width="5" height="5" rx="1" fill="white" opacity="0.5"/>
                <rect x="9" y="9" width="5" height="5" rx="1" fill="white"/>
              </svg>
            </div>
            <span className="text-lg font-bold text-gray-900 dark:text-white tracking-tight">CVMatch</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            {[["How it works","#how"],["Pricing","#pricing"],["FAQ","#faq"]].map(([label, href]) => (
              <a key={label} href={href}
                className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                {label}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <a href="#hero-cta" className="cursor-pointer btn-primary text-sm px-5 py-2.5 rounded-xl">
              Get Started Free
            </a>
          </div>
        </div>
      </nav>

      {/* ── HERO ────────────────────────────────────────────────────────────── */}
      <section className="relative pt-20 pb-28 px-6 overflow-hidden">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full bg-blue-100 dark:bg-blue-900/20 opacity-50 blur-3xl -translate-y-1/3 translate-x-1/3 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] rounded-full bg-blue-50 dark:bg-blue-950/30 opacity-60 blur-3xl translate-y-1/2 -translate-x-1/3 pointer-events-none" />

        <div ref={heroReveal.ref} className="max-w-4xl mx-auto text-center relative">
          <div className={`mb-8 reveal ${heroReveal.visible ? "visible" : ""}`}>
            <span className="pill">✦ AI-Powered Resume Optimization</span>
          </div>

          <h1 className={`text-5xl md:text-7xl font-extrabold leading-[1.08] tracking-tight mb-6 text-gray-900 dark:text-white reveal reveal-delay-1 ${heroReveal.visible ? "visible" : ""}`}>
            Stop Getting Rejected.{" "}
            <span className="text-blue-600 dark:text-blue-400">Start Getting</span>{" "}
            Interviews.
          </h1>

          <p className={`text-gray-500 dark:text-gray-400 text-lg md:text-xl leading-relaxed max-w-2xl mx-auto mb-10 reveal reveal-delay-2 ${heroReveal.visible ? "visible" : ""}`}>
            CVMatch uses AI to tailor your resume to any job description — beating ATS filters and matching exactly what recruiters look for. Upload once, get hired faster.
          </p>

          <div id="hero-cta" className={`flex flex-col sm:flex-row gap-3 justify-center items-center reveal reveal-delay-3 ${heroReveal.visible ? "visible" : ""}`}>
            <a href="#upload" className="btn-primary px-8 py-4 rounded-2xl text-base flex items-center gap-2">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 2v10M5 6l4-4 4 4M3 14h12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Analyze My Resume — Free
            </a>
            <a href="#how" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 underline underline-offset-4 transition-colors">
              See how it works ↓
            </a>
          </div>

          {/* Social proof avatars */}
          <div className={`mt-10 flex justify-center items-center gap-3 reveal reveal-delay-4 ${heroReveal.visible ? "visible" : ""}`}>
            <div className="flex -space-x-2">
              {(["#2563EB","#10B981","#F59E0B","#EF4444","#6366F1"] as const).map((c, i) => (
                <div key={i} className="w-8 h-8 rounded-full border-2 border-white dark:border-gray-800 flex items-center justify-center text-white text-xs font-bold" style={{ background: c }}>
                  {["J","A","M","S","K"][i]}
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              <strong className="text-gray-800 dark:text-gray-200">2,400+</strong> job seekers optimized their resume this week
            </p>
          </div>
        </div>

        {/* Mock score card */}
        <div className={`relative max-w-xl mx-auto mt-16 bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-xl p-6 reveal reveal-delay-5 ${heroReveal.visible ? "visible" : ""}`}>
          <div className="flex items-center gap-4 mb-5">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect x="2" y="2" width="14" height="14" rx="2.5" stroke="white" strokeWidth="1.5"/>
                <path d="M5 7h8M5 10h5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-800 dark:text-gray-100 text-sm truncate">Senior Software Engineer @ Stripe</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Resume analyzed · just now</p>
            </div>
            <div className="relative w-14 h-14 flex-shrink-0">
              <svg width="56" height="56" viewBox="0 0 56 56">
                <circle cx="28" cy="28" r="24" fill="none" stroke="#E5E7EB" strokeWidth="5"/>
                <circle cx="28" cy="28" r="24" fill="none" stroke="#2563EB" strokeWidth="5"
                  strokeLinecap="round" strokeDasharray="150" strokeDashoffset="22"
                  style={{ transform: "rotate(-90deg)", transformOrigin: "center" }}/>
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-gray-800 dark:text-gray-100">85%</span>
            </div>
          </div>

          <div className="space-y-3">
            {[
              { label: "Keyword Match",    val: 88, color: "#10B981" },
              { label: "Skills Alignment", val: 79, color: "#F59E0B" },
              { label: "ATS Score",        val: 91, color: "#10B981" },
            ].map(({ label, val, color }) => (
              <div key={label}>
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                  <span>{label}</span>
                  <span style={{ color }} className="font-semibold">{val}%</span>
                </div>
                <div className="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${val}%`, background: color }} />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 grid grid-cols-2 gap-2">
            <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-3">
              <p className="text-xs text-green-700 dark:text-green-400 font-semibold mb-0.5">✓ Matched skills</p>
              <p className="text-xs text-green-600 dark:text-green-500">React, TypeScript, AWS, CI/CD</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-3">
              <p className="text-xs text-red-600 dark:text-red-400 font-semibold mb-0.5">✗ Missing skills</p>
              <p className="text-xs text-red-500 dark:text-red-400">Kubernetes, Terraform</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── MARQUEE ─────────────────────────────────────────────────────────── */}
      <div className="py-8 border-y border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden transition-colors">
        <div className="flex">
          <div className="marquee">
            {[
              "🎯 72% more interview callbacks",
              "⚡ 3-minute analysis",
              "🤖 Beats ATS filters",
              "🌍 Works for any country or language",
              "📊 Section-by-section breakdown",
              "✅ Trusted by 2,400+ job seekers",
              "🎯 72% more interview callbacks",
              "⚡ 3-minute analysis",
              "🤖 Beats ATS filters",
              "🌍 Works for any country or language",
              "📊 Section-by-section breakdown",
              "✅ Trusted by 2,400+ job seekers",
            ].map((text, i) => (
              <span key={i} className="text-sm text-gray-500 dark:text-gray-400 font-medium flex-shrink-0">{text}</span>
            ))}
          </div>
        </div>
      </div>

      {/* ── HOW IT WORKS ────────────────────────────────────────────────────── */}
      <section id="how" className="py-24 px-6">
        <div ref={howReveal.ref} className="max-w-5xl mx-auto">
          <div className={`text-center mb-16 reveal ${howReveal.visible ? "visible" : ""}`}>
            <div className="pill mb-5 inline-flex">How it works</div>
            <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4">
              Three steps to your{" "}
              <span className="text-blue-600 dark:text-blue-400">next interview</span>
            </h2>
            <p className="text-gray-500 dark:text-gray-400 text-lg max-w-xl mx-auto">
              No fluff. No endless forms. Upload, paste, and get results in under 3 minutes.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { step:"01", icon:"📄", title:"Upload Your Resume",        desc:"Drop your PDF or DOCX. We extract and understand every detail — experience, skills, education.", bg:"bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800",   accent:"text-blue-600 dark:text-blue-400" },
              { step:"02", icon:"📋", title:"Paste the Job Description", desc:"Copy-paste the full job posting. Our AI identifies requirements, keywords, and what matters most.",   bg:"bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800", accent:"text-amber-600 dark:text-amber-400" },
              { step:"03", icon:"✨", title:"Get Your Match Score",       desc:"See exactly how well you fit, what's missing, and actionable fixes to boost your match instantly.",   bg:"bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800", accent:"text-green-600 dark:text-green-400" },
            ].map(({ step, icon, title, desc, bg, accent }, i) => (
              <div key={i} className={`card-hover reveal reveal-delay-${i+1} ${howReveal.visible ? "visible" : ""} ${bg} border rounded-2xl p-7 transition-colors`}>
                <div className={`text-xs font-black tracking-widest mb-4 ${accent}`}>{step}</div>
                <div className="text-3xl mb-4">{icon}</div>
                <h3 className="font-bold text-gray-800 dark:text-gray-100 text-lg mb-2">{title}</h3>
                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── STATS ───────────────────────────────────────────────────────────── */}
      <div className="py-16 px-6 bg-blue-600 dark:bg-blue-800 transition-colors">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { num:2400, suffix:"+",   label:"Resumes analyzed" },
            { num:72,   suffix:"%",   label:"More callbacks reported" },
            { num:3,    suffix:"min", label:"Average analysis time" },
            { num:94,   suffix:"%",   label:"User satisfaction rate" },
          ].map(({ num, suffix, label }) => (
            <div key={label}>
              <p className="text-4xl md:text-5xl font-extrabold text-white mb-1">
                <Counter to={num} suffix={suffix} />
              </p>
              <p className="text-blue-100 text-sm">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── BENEFITS ────────────────────────────────────────────────────────── */}
      <section id="benefits" className="py-24 px-6">
        <div ref={benefitReveal.ref} className="max-w-5xl mx-auto">
          <div className={`text-center mb-16 reveal ${benefitReveal.visible ? "visible" : ""}`}>
            <div className="pill mb-5 inline-flex">Why CVMatch</div>
            <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white">
              Built for the modern{" "}
              <span className="text-blue-600 dark:text-blue-400">job hunt</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon:"🎯", title:"Beat the ATS filter",                   desc:"75% of resumes are rejected before a human ever reads them. CVMatch reverse-engineers ATS scoring so your resume gets through.",                                       border:"border-l-4 border-blue-500" },
              { icon:"⚡", title:"Save hours, not minutes",                desc:"Forget manually tweaking your resume for every job. Get a precise breakdown of exactly what to change and why.",                                                       border:"border-l-4 border-amber-500" },
              { icon:"🌍", title:"Designed for immigrants & career changers", desc:"Navigating a new job market? We highlight transferable skills and help you translate your experience into local terms.",                                              border:"border-l-4 border-green-500" },
              { icon:"📊", title:"Data-driven confidence",                 desc:"Go into every application knowing your match score, strongest selling points, and exactly where to focus your improvements.",                                          border:"border-l-4 border-red-400" },
            ].map(({ icon, title, desc, border }, i) => (
              <div key={i} className={`card-hover bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 ${border} rounded-2xl p-8 pl-7 reveal reveal-delay-${i+1} ${benefitReveal.visible ? "visible" : ""} transition-colors`}>
                <div className="text-3xl mb-4">{icon}</div>
                <h3 className="font-bold text-gray-800 dark:text-gray-100 text-xl mb-2">{title}</h3>
                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ────────────────────────────────────────────────────── */}
      <section className="py-20 px-6 bg-white dark:bg-gray-800 border-y border-gray-200 dark:border-gray-700 transition-colors">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="pill mb-5 inline-flex">What people say</div>
            <h2 className="text-4xl font-extrabold text-gray-900 dark:text-white">
              Real results from{" "}
              <span className="text-blue-600 dark:text-blue-400">real people</span>
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { quote:"I applied to 40 jobs with no luck. After using CVMatch, I landed 3 interviews in one week. The missing skills section was a game-changer.", name:"Marco R.", role:"Software Engineer, moved from Brazil to Canada", avatar:"#2563EB" },
              { quote:"As a recruiter, I now recommend CVMatch to every candidate I coach. The ATS score alone makes it worth it.",                                  name:"Sarah K.", role:"Career Coach, Toronto",                           avatar:"#10B981" },
              { quote:"Changing careers from finance to PM. CVMatch showed me exactly how to reframe my experience. Got my first PM role in 6 weeks.",              name:"James L.", role:"Product Manager @ fintech startup",              avatar:"#F59E0B" },
            ].map(({ quote, name, role, avatar }, i) => (
              <div key={i} className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-7 border border-gray-200 dark:border-gray-700 transition-colors">
                <div className="flex gap-0.5 mb-4">
                  {Array(5).fill(0).map((_, j) => <span key={j} className="text-amber-400 text-sm">★</span>)}
                </div>
                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed mb-6">"{quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center text-white text-xs font-bold" style={{ background: avatar }}>
                    {name[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800 dark:text-gray-100 text-sm">{name}</p>
                    <p className="text-gray-400 dark:text-gray-500 text-xs">{role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PRICING ─────────────────────────────────────────────────────────── */}
      <section id="pricing" className="py-24 px-6">
        <div ref={pricingReveal.ref} className="max-w-4xl mx-auto">
          <div className={`text-center mb-12 reveal ${pricingReveal.visible ? "visible" : ""}`}>
            <div className="pill mb-5 inline-flex">Pricing</div>
            <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4">
              Start free. Unlock{" "}
              <span className="text-blue-600 dark:text-blue-400">everything</span>.
            </h2>
            <p className="text-gray-500 dark:text-gray-400 text-lg">No subscription. Pay once, analyze as many jobs as you need.</p>

            {/* Billing toggle */}
            <div className="flex items-center justify-center gap-3 mt-6">
              <span className={`text-sm font-medium ${!billingAnnual ? "text-gray-800 dark:text-gray-100" : "text-gray-400 dark:text-gray-500"}`}>Monthly</span>
              <button
                onClick={() => setBillingAnnual(!billingAnnual)}
                className={`relative w-12 h-6 rounded-full transition-colors ${billingAnnual ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}
              >
                <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${billingAnnual ? "translate-x-6" : ""}`} />
              </button>
              <span className={`text-sm font-medium flex items-center gap-1.5 ${billingAnnual ? "text-gray-800 dark:text-gray-100" : "text-gray-400 dark:text-gray-500"}`}>
                Annual{" "}
                <span className="bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 text-xs font-bold px-2 py-0.5 rounded-full">Save 40%</span>
              </span>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Free */}
            <div className={`bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl p-8 reveal reveal-delay-1 ${pricingReveal.visible ? "visible" : ""} transition-colors`}>
              <p className="text-xs font-black tracking-widest text-gray-400 dark:text-gray-500 mb-4">FREE</p>
              <p className="text-5xl font-extrabold text-gray-900 dark:text-white mb-1">$0</p>
              <p className="text-gray-400 dark:text-gray-500 text-sm mb-8">Forever free · no credit card</p>
              <ul className="space-y-3 mb-8">
                {["1 resume analysis per day","Overall match score","Keyword matching","Basic skill gap overview"].map(item => (
                  <li key={item} className="flex items-center gap-2.5 text-sm text-gray-600 dark:text-gray-300">
                    <span className="w-5 h-5 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 text-xs flex-shrink-0">✓</span>
                    {item}
                  </li>
                ))}
                {["Section-by-section breakdown","Strengths & gaps analysis","Priority support"].map(item => (
                  <li key={item} className="flex items-center gap-2.5 text-sm text-gray-300 dark:text-gray-600 line-through">
                    <span className="w-5 h-5 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-300 dark:text-gray-600 text-xs flex-shrink-0">✗</span>
                    {item}
                  </li>
                ))}
              </ul>
              <button className="cursor-pointer btn-outline w-full py-3.5 rounded-xl text-sm">
                Get Started Free
              </button>
            </div>

            {/* Pro */}
            <div className={`relative bg-blue-600 dark:bg-blue-700 border-2 border-blue-600 dark:border-blue-700 rounded-2xl p-8 text-white reveal reveal-delay-2 ${pricingReveal.visible ? "visible" : ""} transition-colors`}>
              <div className="absolute top-5 right-5">
                <span className="bg-amber-400 text-gray-900 text-xs font-black px-3 py-1 rounded-full uppercase tracking-wide">Most Popular</span>
              </div>
              <p className="text-xs font-black tracking-widest text-blue-200 mb-4">UNLOCK ALL</p>
              <p className="text-5xl font-extrabold mb-1">{billingAnnual ? "$3" : "$5"}</p>
              <p className="text-blue-200 text-sm mb-8">{billingAnnual ? "per month, billed annually" : "one-time unlock"}</p>
              <ul className="space-y-3 mb-8">
                {["Unlimited resume analyses","Full match score breakdown","Section-by-section similarity","Detailed skill gap analysis","Strengths & improvement areas","Export PDF report","Priority support"].map(item => (
                  <li key={item} className="flex items-center gap-2.5 text-sm text-blue-100">
                    <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-white text-xs flex-shrink-0">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
              <button className="cursor-pointer w-full py-3.5 rounded-xl bg-white text-blue-600 font-bold text-sm hover:bg-blue-50 transition-colors">
                Unlock for {billingAnnual ? "$3/mo" : "$5"}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ──────────────────────────────────────────────────────── */}
      <section id="upload" className="py-20 px-6">
        <div className="max-w-3xl mx-auto bg-blue-600 dark:bg-blue-700 rounded-3xl p-12 text-center text-white relative overflow-hidden transition-colors">
          <div className="absolute inset-0 opacity-20 pointer-events-none"
            style={{ backgroundImage: "radial-gradient(circle at 20% 50%, #93C5FD 0%, transparent 55%), radial-gradient(circle at 80% 50%, #1E3A8A 0%, transparent 55%)" }}
          />
          <div className="relative">
            <h2 className="text-4xl md:text-5xl font-extrabold mb-4 leading-tight">
              Your next interview<br />starts <span className="text-blue-200">right now</span>
            </h2>
            <p className="text-blue-100 text-lg mb-8 max-w-lg mx-auto">
              Upload your resume, paste a job description, and get an AI-powered analysis in under 3 minutes. It's free.
            </p>
            <a href="/app" className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-white text-blue-600 font-bold text-base hover:bg-blue-50 transition-colors">
              Analyze My Resume — It's Free
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </a>
            <p className="text-blue-200 text-xs mt-4">No sign-up required · Works with PDF &amp; DOCX</p>
          </div>
        </div>
      </section>

      {/* ── FAQ ─────────────────────────────────────────────────────────────── */}
      <section id="faq" className="py-20 px-6 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 transition-colors">
        <div ref={faqReveal.ref} className="max-w-2xl mx-auto">
          <div className={`text-center mb-12 reveal ${faqReveal.visible ? "visible" : ""}`}>
            <div className="pill mb-5 inline-flex">FAQ</div>
            <h2 className="text-4xl font-extrabold text-gray-900 dark:text-white">
              Questions?{" "}
              <span className="text-blue-600 dark:text-blue-400">We've got answers.</span>
            </h2>
          </div>
          <div className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 px-8 py-2 shadow-sm reveal reveal-delay-1 ${faqReveal.visible ? "visible" : ""} transition-colors`}>
            {[
              { q:"Is CVMatch actually free?",            a:"Yes! You can analyze one resume per day completely free, including the match score and keyword analysis. The $5 unlock gives you unlimited analyses plus the full breakdown — section-by-section scores, skill gaps, strengths, and more." },
              { q:"What file formats are supported?",     a:"We support PDF and DOCX files up to 5MB. For best results, make sure your resume is text-based (not a scanned image)." },
              { q:"Does it work for any job or industry?",a:"Absolutely. CVMatch works for any job description in any industry — tech, finance, healthcare, marketing, and more. It also works across countries and languages." },
              { q:"How is my score calculated?",          a:"We use a combination of semantic AI similarity (how well the meaning of your resume matches the job), keyword TF-IDF matching, and section-specific analysis (skills, experience, education)." },
              { q:"Is my resume data private?",           a:"Yes. We process your resume only to generate the analysis and never store, share, or use it to train models. Your data is yours." },
              { q:"What if I'm an immigrant or career changer?", a:"CVMatch is especially valuable for you. We identify transferable skills, highlight gaps you might not be aware of, and help you understand what local employers are actually looking for." },
            ].map((item) => <FAQItem key={item.q} {...item} />)}
          </div>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────────────────────────────────── */}
      <footer className="py-12 px-6 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="2" width="5" height="5" rx="1" fill="white"/>
                <rect x="9" y="2" width="5" height="5" rx="1" fill="white" opacity="0.5"/>
                <rect x="2" y="9" width="5" height="5" rx="1" fill="white" opacity="0.5"/>
                <rect x="9" y="9" width="5" height="5" rx="1" fill="white"/>
              </svg>
            </div>
            <span className="font-bold text-gray-800 dark:text-gray-100">CVMatch</span>
          </div>
          <p className="text-gray-400 dark:text-gray-500 text-xs text-center">
            Analysis generated through natural language processing · Results are indicative and do not replace human evaluation.
          </p>
          <div className="flex gap-6">
            {["Privacy","Terms","Support"].map(link => (
              <a key={link} href="#" className="text-xs text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">{link}</a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}