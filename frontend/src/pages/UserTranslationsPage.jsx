import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCookies } from 'react-cookie';

const UserTranslationsPage = () => {
    const [translations, setTranslations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState({
        sourceLang: '',
        targetLang: '',
    });
    const [appliedFilters, setAppliedFilters] = useState(filters);
    const [sortField, setSortField] = useState('created_at');
    const [sortOrder, setSortOrder] = useState('desc');
    const [cookies] = useCookies(['auth']);

    const fetchTranslations = async (customFilters = appliedFilters) => {
        setLoading(true);
        setError('');

        try {
            const sourceLang = customFilters.sourceLang?.toUpperCase().trim();
            const targetLang = customFilters.targetLang?.toUpperCase().trim();

            let url = `http://localhost:8000/api/translations/my_translations/?ordering=${sortOrder === 'asc' ? '' : '-'}${sortField}`;

            if (sourceLang) url += `&source_lang=${sourceLang}`;
            if (targetLang) url += `&target_lang=${targetLang}`;

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${cookies.auth}`,
                },
            });

            if (!response.ok) throw new Error('Failed to fetch translations');
            const data = await response.json();
            setTranslations(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTranslations();
    }, [sortField, sortOrder, cookies.auth]);

    const handleApplyFilters = () => {
        setAppliedFilters(filters);
        fetchTranslations(filters);
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    const handleSort = (field) => {
        if (field === sortField) {
            setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
        } else {
            setSortField(field);
            setSortOrder('desc');
        }
    };

    if (loading) return <div>Loading translations...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="user-translations-page">
            <h1>My Translations</h1>

            <div className="filters">
                <h2>Filter by Language</h2>
                <div className="filter-group">
                    <label>Source Language:</label>
                    <input
                        type="text"
                        name="sourceLang"
                        value={filters.sourceLang}
                        onChange={handleFilterChange}
                        placeholder="e.g., en"
                    />
                </div>
                <div className="filter-group">
                    <label>Target Language:</label>
                    <input
                        type="text"
                        name="targetLang"
                        value={filters.targetLang}
                        onChange={handleFilterChange}
                        placeholder="e.g., uk"
                    />
                </div>
                <button onClick={handleApplyFilters}>Apply Filters</button>
            </div>

            <div className="translations-list">
                {translations.length === 0 ? (
                    <div style={{ marginTop: '20px' }}>No translations found.</div>
                ) : (
                    <table>
                        <thead>
                        <tr>
                            <th onClick={() => handleSort('id')}>ID</th>
                            <th onClick={() => handleSort('source_lang')}>Source</th>
                            <th onClick={() => handleSort('target_lang')}>Target</th>
                            <th onClick={() => handleSort('created_at')}>Date</th>
                            <th onClick={() => handleSort('payment__amount')}>Amount</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                        </thead>
                        <tbody>
                        {translations.map((t) => (
                            <tr key={t.id}>
                                <td>{t.id}</td>
                                <td>{t.source_lang}</td>
                                <td>{t.target_lang}</td>
                                <td>{new Date(t.created_at).toLocaleString()}</td>
                                <td>{t.payment?.amount ?? '-'} UAH</td>
                                <td>{t.payment?.status ?? '-'}</td>
                                <td>
                                    <Link to={`/translation/${t.id}`}>View</Link>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default UserTranslationsPage;
