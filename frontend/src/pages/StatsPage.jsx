import React, { useState, useEffect } from 'react';
import { useCookies } from 'react-cookie';

const StatsPage = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState({
        user: '',
        dateFrom: '',
        dateTo: '',
    });
    const [sortField, setSortField] = useState('created_at');
    const [sortOrder, setSortOrder] = useState('desc');
    const [cookies] = useCookies(['auth']);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/stats/', {
                    headers: {
                        'Authorization': `Token ${cookies.auth}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) throw new Error('Failed to fetch stats');
                const data = await response.json();
                setStats(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, [cookies]);

    const handleApplyFilters = async () => {
        setLoading(true);
        setError('');
        try {
            let url = `http://localhost:8000/api/stats/?ordering=${sortOrder === 'asc' ? '' : '-'}${sortField}`;

            if (filters.user) url += `&user=${filters.user}`;
            if (filters.dateFrom) url += `&date_from=${filters.dateFrom}`;
            if (filters.dateTo) url += `&date_to=${filters.dateTo}`;

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Token ${cookies.auth}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) throw new Error('Failed to fetch stats');

            const data = await response.json();
            setStats(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
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



    if (loading) return <div>Loading...</div>;
    if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

    return (
        <div className="stats-page">
            <h1>Admin Statistics</h1>

            {stats?.daily_stats && (
                <div
                    className="stats-summary"
                    style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}
                >
                    <div className="stat-card">
                        <h3>Total Translations</h3>
                        <p>{stats.daily_stats.total_translations}</p>
                    </div>
                    <div className="stat-card">
                        <h3>Total Revenue</h3>
                        <p>{stats.daily_stats.total_revenue} UAH</p>
                    </div>
                    <div className="stat-card">
                        <h3>Average Order Value</h3>
                        <p>{stats.daily_stats.average_check} UAH</p>
                    </div>
                    <div className="stat-card">
                        <h3>Registered Users</h3>
                        <p>{stats.daily_stats.total_users}</p>
                    </div>
                    <div className="stat-card">
                        <h3>Active Users</h3>
                        <p>{stats.daily_stats.users_with_translations}</p>
                    </div>
                </div>
            )}

            <div className="filters" style={{ marginBottom: '20px' }}>
                <h2>Filter Translations</h2>
                <div className="filter-group">
                    <label>User ID:</label>
                    <input
                        type="text"
                        name="user"
                        value={filters.user}
                        onChange={handleFilterChange}
                        placeholder="User ID"
                    />
                </div>
                <div className="filter-group">
                    <label>From Date:</label>
                    <input
                        type="date"
                        name="dateFrom"
                        value={filters.dateFrom}
                        onChange={handleFilterChange}
                    />
                </div>
                <div className="filter-group">
                    <label>To Date:</label>
                    <input
                        type="date"
                        name="dateTo"
                        value={filters.dateTo}
                        onChange={handleFilterChange}
                    />
                </div>

                <button onClick={handleApplyFilters}>Apply Filters</button>
            </div>

            <div className="translations-table">
                <h2>All Translations</h2>
                {stats?.translations?.length > 0 ? (
                    <table border="1" cellPadding="5" cellSpacing="0">
                        <thead>
                        <tr>
                            <th
                                onClick={() => handleSort('id')}
                                style={{ cursor: 'pointer' }}
                            >
                                ID
                            </th>
                            <th
                                onClick={() => handleSort('user__username')}
                                style={{ cursor: 'pointer' }}
                            >
                                User
                            </th>
                            <th
                                onClick={() => handleSort('source_lang')}
                                style={{ cursor: 'pointer' }}
                            >
                                Source Lang
                            </th>
                            <th
                                onClick={() => handleSort('target_lang')}
                                style={{ cursor: 'pointer' }}
                            >
                                Target Lang
                            </th>
                            <th
                                onClick={() => handleSort('created_at')}
                                style={{ cursor: 'pointer' }}
                            >
                                Date
                            </th>
                            <th>Price</th>
                        </tr>
                        </thead>
                        <tbody>
                        {stats.translations.map((t) => (
                            <tr key={t.id}>
                                <td>{t.id}</td>
                                <td>{ t.user.id}</td>
                                <td>{t.source_lang}</td>
                                <td>{t.target_lang}</td>
                                <td>{new Date(t.created_at).toLocaleString()}</td>
                                <td>{t.payment?.amount ?? '-'}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No translations found.</p>
                )}
            </div>
        </div>
    );
};

export default StatsPage;
