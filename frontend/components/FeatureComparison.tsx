"use client";

import React from "react";

interface Feature {
  name: string;
  free: {
    available: boolean;
    limited?: boolean;
    description: string;
  };
  premium: {
    available: boolean;
    description: string;
  };
}

const features: Feature[] = [
  {
    name: "CV Upload",
    free: {
      available: true,
      limited: true,
      description: "1 CV per day",
    },
    premium: {
      available: true,
      description: "Unlimited uploads",
    },
  },
  {
    name: "Match Analysis",
    free: {
      available: true,
      limited: true,
      description: "Basic: Overall score, keywords, simple summary",
    },
    premium: {
      available: true,
      description: "Full: Section-by-section, skills, experience, education, semantic alignment",
    },
  },
  {
    name: "Recommendations",
    free: {
      available: true,
      limited: true,
      description: "Max 5 skills per category",
    },
    premium: {
      available: true,
      description: "Full insights & improvement suggestions",
    },
  },
  {
    name: "Analysis History",
    free: {
      available: false,
      description: "Not available",
    },
    premium: {
      available: true,
      description: "Full access to past analyses",
    },
  },
  {
    name: "PDF Report Download",
    free: {
      available: false,
      description: "Not available",
    },
    premium: {
      available: true,
      description: "Download detailed PDF reports",
    },
  },
  {
    name: "Backup Analysis",
    free: {
      available: true,
      limited: true,
      description: "Limited backup storage",
    },
    premium: {
      available: true,
      description: "Full backup with cloud sync",
    },
  },
  {
    name: "Strengths & Gaps",
    free: {
      available: true,
      limited: true,
      description: "Partial analysis",
    },
    premium: {
      available: true,
      description: "Comprehensive analysis with actionable insights",
    },
  },
];

export default function FeatureComparison() {
  return (
    <section className="py-16 px-4 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Choose Your Perfect Plan
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            Unlock the full potential of CVMatch with Premium. Get deeper insights,
            unlimited analyses, and advanced features to land your dream job.
          </p>
        </div>

        {/* Comparison Table */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-200 dark:border-slate-700">
          {/* Table Header */}
          <div className="grid grid-cols-3 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-700 border-b border-slate-200 dark:border-slate-600">
            <div className="p-6 font-semibold text-slate-700 dark:text-slate-200 text-lg">
              Features
            </div>
            <div className="p-6 text-center border-l border-slate-200 dark:border-slate-600">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-200 dark:bg-slate-600 rounded-full">
                <span className="text-2xl">🆓</span>
                <span className="font-bold text-slate-700 dark:text-slate-200">Free</span>
              </div>
            </div>
            <div className="p-6 text-center border-l border-slate-200 dark:border-slate-600 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full shadow-lg">
                <span className="text-2xl">⭐</span>
                <span className="font-bold text-white">Premium</span>
              </div>
            </div>
          </div>

          {/* Feature Rows */}
          {features.map((feature, index) => (
            <div
              key={feature.name}
              className={`grid grid-cols-3 ${
                index % 2 === 0
                  ? "bg-white dark:bg-slate-800"
                  : "bg-slate-50/50 dark:bg-slate-750"
              } border-b border-slate-100 dark:border-slate-700 last:border-b-0 hover:bg-blue-50/50 dark:hover:bg-slate-700/50 transition-colors`}
            >
              {/* Feature Name */}
              <div className="p-6 flex items-center gap-3">
                <span className="text-xl font-semibold text-slate-800 dark:text-slate-100">
                  {feature.name}
                </span>
              </div>

              {/* Free Tier */}
              <div className="p-6 border-l border-slate-200 dark:border-slate-600 flex flex-col items-center justify-center">
                {feature.free.available ? (
                  <div className="flex flex-col items-center gap-2">
                    {feature.free.limited ? (
                      <>
                        <span className="text-2xl" title="Limited">⚡</span>
                        <span className="text-sm font-medium text-amber-600 dark:text-amber-400">
                          Limited
                        </span>
                      </>
                    ) : (
                      <>
                        <span className="text-2xl" title="Available">✅</span>
                        <span className="text-sm font-medium text-green-600 dark:text-green-400">
                          Available
                        </span>
                      </>
                    )}
                    <span className="text-xs text-slate-500 dark:text-slate-400 text-center mt-1">
                      {feature.free.description}
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <span className="text-2xl" title="Locked">🔒</span>
                    <span className="text-sm font-medium text-slate-400 dark:text-slate-500">
                      Locked
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500 text-center mt-1">
                      {feature.free.description}
                    </span>
                  </div>
                )}
              </div>

              {/* Premium Tier */}
              <div className="p-6 border-l border-slate-200 dark:border-slate-600 flex flex-col items-center justify-center bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-900/20 dark:to-purple-900/20">
                <div className="flex flex-col items-center gap-2">
                  <span className="text-2xl" title="Available">✅</span>
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">
                    Full Access
                  </span>
                  <span className="text-xs text-slate-600 dark:text-slate-300 text-center mt-1">
                    {feature.premium.description}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-xl">✅</span>
            <span className="text-slate-600 dark:text-slate-300">Available</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xl">⚡</span>
            <span className="text-slate-600 dark:text-slate-300">Limited</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xl">🔒</span>
            <span className="text-slate-600 dark:text-slate-300">Locked</span>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-12 text-center">
          <div className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 p-[2px] rounded-2xl">
            <div className="bg-white dark:bg-slate-800 rounded-2xl px-8 py-6">
              <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-3">
                Ready to Supercharge Your Job Search?
              </h3>
              <p className="text-slate-600 dark:text-slate-300 mb-6 max-w-md mx-auto">
                Upgrade to Premium and unlock unlimited analyses, detailed insights,
                and professional reports to stand out from the competition.
              </p>
              <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200">
                🚀 Upgrade to Premium
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
