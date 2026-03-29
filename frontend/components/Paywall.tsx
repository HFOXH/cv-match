"use client";

import { useUser, SignInButton, SignUpButton } from "@clerk/nextjs";
import { ReactNode } from "react";

interface PaywallProps {
  children: ReactNode;
}

export default function Paywall({ children }: PaywallProps) {
  const { isSignedIn, user } = useUser();

  // Check if user has subscription (you can customize this logic based on your Clerk setup)
  // For now, we'll check if user is signed in - you can add subscription check later
  const hasSubscription = isSignedIn; // Replace with actual subscription check

  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 antialiased overflow-x-hidden transition-colors duration-300">
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

          .card-hover { transition: transform 0.22s ease, box-shadow 0.22s ease; }
          .card-hover:hover { transform: translateY(-3px); box-shadow: 0 14px 28px -8px rgba(37,99,235,0.13); }
        `}</style>

        <div className="max-w-4xl mx-auto px-6 py-24">
          <div className="text-center mb-12">
            <div className="pill mb-5 inline-flex">🔒 Premium Feature</div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4">
              Unlock <span className="text-blue-600 dark:text-blue-400">Full Analysis</span>
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-lg max-w-xl mx-auto">
              Sign in to access the resume analyzer and get detailed match scores, skill breakdowns, and personalized recommendations.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-12">
            {/* Free Features */}
            <div className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl p-8 card-hover transition-colors">
              <p className="text-xs font-black tracking-widest text-gray-400 dark:text-gray-500 mb-4">WITHOUT ACCOUNT</p>
              <ul className="space-y-3 mb-8">
                {[
                  "View landing page",
                  "See pricing information",
                  "Read testimonials"
                ].map(item => (
                  <li key={item} className="flex items-center gap-2.5 text-sm text-gray-600 dark:text-gray-300">
                    <span className="w-5 h-5 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-400 dark:text-gray-500 text-xs flex-shrink-0">✓</span>
                    {item}
                  </li>
                ))}
                {[
                  "Resume analysis",
                  "Match scoring",
                  "Skill breakdown",
                  "Personalized tips"
                ].map(item => (
                  <li key={item} className="flex items-center gap-2.5 text-sm text-gray-300 dark:text-gray-600 line-through">
                    <span className="w-5 h-5 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-300 dark:text-gray-600 text-xs flex-shrink-0">✗</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* With Account */}
            <div className="relative bg-blue-600 dark:bg-blue-700 border-2 border-blue-600 dark:border-blue-700 rounded-2xl p-8 text-white card-hover transition-colors">
              <div className="absolute top-5 right-5">
                <span className="bg-amber-400 text-gray-900 text-xs font-black px-3 py-1 rounded-full uppercase tracking-wide">Recommended</span>
              </div>
              <p className="text-xs font-black tracking-widest text-blue-200 mb-4">WITH FREE ACCOUNT</p>
              <ul className="space-y-3 mb-8">
                {[
                  "1 resume analysis per day",
                  "Overall match score",
                  "Keyword matching",
                  "Basic skill gap overview"
                ].map(item => (
                  <li key={item} className="flex items-center gap-2.5 text-sm text-blue-100">
                    <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-white text-xs flex-shrink-0">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
              <SignUpButton>
                <button className="cursor-pointer w-full py-3.5 rounded-xl text-sm font-bold bg-white text-blue-600 hover:bg-blue-50 transition-colors">
                  Create Free Account
                </button>
              </SignUpButton>
            </div>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Already have an account?
            </p>
            <SignInButton>
              <button className="cursor-pointer btn-outline px-8 py-3 rounded-xl text-sm">
                Sign In
              </button>
            </SignInButton>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 pt-8 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-wrap justify-center gap-8 text-center">
              {[
                { icon: "🔒", text: "Secure & Private" },
                { icon: "⚡", text: "Instant Access" },
                { icon: "💳", text: "No Credit Card Required" },
                { icon: "🌍", text: "Works Worldwide" }
              ].map(({ icon, text }) => (
                <div key={text} className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <span className="text-lg">{icon}</span>
                  {text}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // User is signed in, show the content
  return <>{children}</>;
}
