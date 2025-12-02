import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/auth');
    };

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <Link to="/">Translation App</Link>
            </div>

            {isAuthenticated && (
                <div className="navbar-links">
                    <Link to="/">Home</Link>
                    <Link to="/my_translations">My Translations</Link>
                    {user && (user.is_admin || user.is_root) && <Link to="/stats">Stats</Link>}
                    <button onClick={handleLogout}>Logout</button>
                    <span className="username">{user.username}</span>
                </div>
            )}
        </nav>
    );
};

export default Navbar;