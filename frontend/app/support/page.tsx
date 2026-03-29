import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

export default function SupportPage() {
    return (
        <div>
            <Navbar />
            <main className="max-w-3xl mx-auto px-6 py-16 text-sm text-gray-700 dark:text-gray-300">
                <h1 className="text-3xl font-bold mb-6">Support</h1>

                <p className="mb-4">
                    Need help? We're here for you.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Contact</h2>
                <p className="mb-4">
                    Email us at: <span className="font-medium">support@cvmatch.ai</span>
                </p>

                <h2 className="font-semibold mt-6 mb-2">Common Issues</h2>
                <ul className="list-disc ml-6 space-y-2">
                    <li>File upload not working → Ensure it's PDF or DOCX under 5MB</li>
                    <li>No analysis result → Check internet connection or retry</li>
                    <li>Payment issues → Contact support with your email</li>
                </ul>

                <h2 className="font-semibold mt-6 mb-2">Response Time</h2>
                <p className="mb-4">
                    We usually respond within 24–48 hours.
                </p>
            </main>
            <Footer />
        </div>
    );
}