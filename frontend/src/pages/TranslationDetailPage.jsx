import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCookies } from 'react-cookie';

const TranslationDetailPage = () => {
    const { id } = useParams();
    const [translation, setTranslation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { user } = useAuth();
    const [cookies] = useCookies(['auth']);

    useEffect(() => {
        const fetchTranslation = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/translations/${id}/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Token ${cookies.auth}`,
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch translation');
                }

                const data = await response.json();

                if (!user.is_admin && user.id !== data.user.id) {
                    throw new Error('You do not have permission to view this translation');
                }

                setTranslation(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchTranslation();
    }, []);

    useEffect(() => {
        const fetchPayment = async (paymentId) => {
            try {
                const response = await fetch(`http://localhost:8000/api/payments/${paymentId}/`, {
                    headers: {
                        'Authorization': `Token ${cookies.auth}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) throw new Error('Failed to fetch payment');
                const paymentData = await response.json();
                setTranslation((prev) => ({ ...prev, payment: paymentData }));
            } catch (err) {
                console.error(err);
            }
        };

        if (translation && typeof translation.payment === 'number') {
            fetchPayment(translation.payment);
        }
    }, [translation, cookies.auth]);



    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!translation) return <div>Translation not found</div>;

    return (
        <div className="translation-detail-page">
            <h1>Translation Details</h1>

            <div className="translation-info">
                <div className="info-row">
                    <span className="label">ID:</span>
                    <span>{translation.id}</span>
                </div>
                <div className="info-row">
                    <span className="label">Date:</span>
                    <span>{new Date(translation.created_at).toLocaleString()}</span>
                </div>
                <div className="info-row">
                    <span className="label">User:</span>
                    <span>{translation.user.username}</span>
                </div>
                <div className="info-row">
                    <span className="label">Payment:</span>
                    <span>{translation.payment.amount} UAH ({translation.payment.status})</span>
                </div>
                <div className="info-row">
                    <span className="label">Languages:</span>
                    <span>{translation.source_lang} → {translation.target_lang}</span>
                </div>
            </div>

            <div className="translation-content">
                <div className="source-text">
                    <h3>Original Text</h3>
                    <p>{translation.source_text}</p>
                </div>
                <div className="translated-text">
                    <h3>Translation</h3>
                    <p>{translation.translated_text}</p>
                </div>
            </div>
        </div>
    );
};

export default TranslationDetailPage;