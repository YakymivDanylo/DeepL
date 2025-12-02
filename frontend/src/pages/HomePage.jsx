import React, { useState } from 'react';
import { useAuth } from "../context/AuthContext";
import { useCookies } from 'react-cookie';

const languages = [
    { code: 'en', name: "English" },
    { code: 'uk', name: "Ukrainian" },
    { code: 'fr', name: "French" },
    { code: 'gr', name: "German" },
    { code: 'es', name: "Spanish" },
];

const HomePage = () => {
    const [text, setText] = useState("");
    const [targetLang, setTargetLang] = useState("en");
    const [sourceLang, setSourceLang] = useState("en");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState('');
    const { user } = useAuth();
    const [cookies] = useCookies(['auth']);

    const calculatePrice = (text) => {
        return Math.ceil(text.length / 10);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (!text.trim()) {
            setError('Please enter text to translate');
            return;
        }

        if (sourceLang === targetLang) {
            setError("Source and target languages must be different");
            return;
        }

        setIsLoading(true);

        try {
            const res = await fetch("http://localhost:8000/api/payments/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Token ${cookies.auth}`,
                },
                credentials: "include",
                body: JSON.stringify({
                    source_text: text,
                    source_lang: sourceLang,
                    target_lang: targetLang,
                }),
            });

            const data = await res.json();

            if (!res.ok) {
                const message = data?.error || data?.detail || "Failed to create payment";
                throw new Error(message);
            }

            window.open(data.payment_url, "_blank");
            setSuccess(`Please complete the payment — translation will be emailed to ${user.email}`);
            setText('');
        } catch (error) {
            setError(error.message || "Something went wrong");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="home-page">
            <h1>Translate Text</h1>
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="text">Text to translate</label>
                    <textarea
                        id="text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        rows="5"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="sourceLang">Source language</label>
                    <select
                        id="sourceLang"
                        value={sourceLang}
                        onChange={(e) => setSourceLang(e.target.value)}
                    >
                        {languages.map((lang) => (
                            <option key={lang.code} value={lang.code}>
                                {lang.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="targetLang">Target language</label>
                    <select
                        id="targetLang"
                        value={targetLang}
                        onChange={(e) => setTargetLang(e.target.value)}
                    >
                        {languages.map((lang) => (
                            <option key={lang.code} value={lang.code}>
                                {lang.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="price-info">
                    Estimated price: {calculatePrice(text)} UAH
                </div>

                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Pay & Translate'}
                </button>
            </form>
        </div>
    );
};

export default HomePage;
