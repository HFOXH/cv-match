import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

export default function TermsPage() {
    return (
        <div>
            <Navbar />
            <main className="max-w-3xl mx-auto px-6 py-16 text-sm text-gray-700 dark:text-gray-300">
                <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>

                <p className="mb-4">
                    By using CVMatch, you agree to the following terms.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Use of Service</h2>
                <p className="mb-4">
                    CVMatch provides AI-based analysis to compare CVs with job descriptions. Results are indicative only.
                </p>

                <h2 className="font-semibold mt-6 mb-2">User Responsibility</h2>
                <p className="mb-4">
                    You are responsible for the data you upload and how you use the results.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Payments</h2>
                <p className="mb-4">
                    Premium features require payment. All purchases are final unless required by law.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Limitation of Liability</h2>
                <p className="mb-4">
                    CVMatch is not responsible for job outcomes or decisions based on the analysis.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Termination</h2>
                <p className="mb-4">
                    We reserve the right to suspend accounts that violate these terms.
                </p>

                <p className="mt-8 text-xs text-gray-400">
                    Last updated: 2026
                </p>
            </main>
            <Footer />
        </div>
    );
}