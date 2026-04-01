import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

export default function PrivacyPage() {
    return (
        <div>
            <Navbar />
            <main className="max-w-3xl mx-auto px-6 py-16 text-sm text-gray-700 dark:text-gray-300">
                <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>

                <p className="mb-4">
                    CVMatch values your privacy. This policy explains how we collect, use, and protect your information.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Information We Collect</h2>
                <p className="mb-4">
                    We collect the data you provide, including your CV, job descriptions, and account details.
                </p>

                <h2 className="font-semibold mt-6 mb-2">How We Use Data</h2>
                <p className="mb-4">
                    Your data is used to analyze compatibility between your CV and job descriptions and improve our service.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Data Storage</h2>
                <p className="mb-4">
                    We store your data securely and do not sell your personal information to third parties.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Third-Party Services</h2>
                <p className="mb-4">
                    We may use third-party services such as authentication and payment providers to operate our platform.
                </p>

                <h2 className="font-semibold mt-6 mb-2">Your Rights</h2>
                <p className="mb-4">
                    You may request deletion of your data at any time by contacting support.
                </p>

                <p className="mt-8 text-xs text-gray-400">
                    Last updated: 2026
                </p>
            </main>
            <Footer />
        </div>
    );
}