"use client";

import { useUser, SignInButton, UserButton, ClerkProvider } from "@clerk/nextjs";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const { isSignedIn, user } = useUser();

  return (
    <nav className="sticky top-0 z-50 bg-gray-50/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 transition-colors">
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        {/* Logo */}
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

        {/* Links */}
        <div className="hidden md:flex items-center gap-8">
          {[
            ["How it works", "#how"],
            ["Pricing", "#pricing"],
            ["FAQ", "#faq"]
          ].map(([label, href]) => (
            <a key={label} href={href}
              className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              {label}
            </a>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <ThemeToggle />
          {!isSignedIn ? (
            <SignInButton>
              <button className="cursor-pointer btn-primary text-sm px-5 py-2.5 rounded-xl">
                Get Started
              </button>
            </SignInButton>
          ) : (
            <UserButton />
          )}
        </div>
      </div>
    </nav>
  );
}