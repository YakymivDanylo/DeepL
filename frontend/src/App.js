import React from 'react';
import {BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
import {AuthProvider, useAuth} from './context/AuthContext';
import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';
import UserTranslationsPage from './pages/UserTranslationsPage';
import TranslationDetailPage from './pages/TranslationDetailPage';
import StatsPage from './pages/StatsPage';
import Navbar from './components/Navbar';
import './App.css';
import {CookiesProvider} from "react-cookie";

const PrivateRoute = ({children, adminOnly = false}) => {
    const {user, isAuthenticated} = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/auth" replace/>;
    }

    if (adminOnly && !(user.is_admin || user.is_root)) {
        return <Navigate to="/"/>;
    }

    return children;
};

function App() {
    return (
        <CookiesProvider>
            <Router>
                <AuthProvider>

                    <div className="app">
                        <Navbar/>
                        <div className="content">
                            <Routes>
                                <Route path="/auth" element={<AuthPage/>}/>
                                <Route path="/" element={
                                    <PrivateRoute>
                                        <HomePage/>
                                    </PrivateRoute>
                                }/>
                                <Route path="/my_translations" element={
                                    <PrivateRoute>
                                        <UserTranslationsPage/>
                                    </PrivateRoute>
                                }/>
                                <Route path="/translation/:id" element={
                                    <PrivateRoute>
                                        <TranslationDetailPage/>
                                    </PrivateRoute>
                                }/>
                                <Route path="/stats" element={
                                    <PrivateRoute adminOnly>
                                        <StatsPage/>
                                    </PrivateRoute>
                                }/>
                            </Routes>
                        </div>
                    </div>
                </AuthProvider>
            </Router>

        </CookiesProvider>
    );
}


export default App;