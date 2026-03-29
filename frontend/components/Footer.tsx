"use client";

export default function Footer() {
    return (
        <footer className="py-12 px-6 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors">
            <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center">
                        <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
                            <rect x="2" y="2" width="5" height="5" rx="1" fill="white" />
                            <rect x="9" y="2" width="5" height="5" rx="1" fill="white" opacity="0.5" />
                            <rect x="2" y="9" width="5" height="5" rx="1" fill="white" opacity="0.5" />
                            <rect x="9" y="9" width="5" height="5" rx="1" fill="white" />
                        </svg>
                    </div>
                    <span className="font-bold text-gray-800 dark:text-gray-100">CVMatch</span>
                </div>
                <p className="text-gray-400 dark:text-gray-500 text-xs text-center">
                    Analysis generated through natural language processing · Results are indicative and do not replace human evaluation.
                </p>
                <div className="flex gap-6">
                    {["Privacy", "Terms", "Support"].map(link => (
                        <a key={link} href="#" className="text-xs text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">{link}</a>
                    ))}
                </div>
            </div>
        </footer>
    );
}