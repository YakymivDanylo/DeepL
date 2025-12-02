import React, { createContext, useContext, useState, useEffect } from 'react';
import { useCookies } from "react-cookie";
import {data, useNavigate} from "react-router-dom";
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [cookies, setCookie, removeCookie] = useCookies(['auth']);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate()
    const isAuthenticated = !!user;

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await fetch("http://localhost:8000/api/users/profile/", {
                    headers: {
                        Authorization: `Token ${cookies.auth}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setUser(data);
                } else {
                    setUser(null);
                    removeCookie('auth');
                }
            } catch (error) {
                console.error("Auth check failed: ", error);
                setUser(null);
                removeCookie('auth');
            } finally {
                setLoading(false);
            }
        };

        if (cookies.auth) {
            checkAuth();
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (username, password) => {
        try {
            const response = await fetch("http://localhost:8000/api/users/login/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();

            if (response.ok) {
                setCookie('auth', data.token, { path: '/', maxAge: 60 * 60 * 24 * 7 });
                setUser({ id: data.user_id, username: data.username, email: data.email });
                return { success: true, token: data.token, user: { id: data.user_id, username: data.username, email: data.email } };
            } else {
                return { success: false, error: data };
            }
        } catch (error) {
            return { success: false, error: { detail: error.message || "Network error" } };
        }
    };


    const register = async (email, username, password, password2) => {
        try {
            const response = await fetch("http://localhost:8000/api/users/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, username, password, password2 }),
            });
            const data = await response.json();

            if (response.ok) {
                setCookie('auth', data.token, { path: '/', maxAge: 60 * 60 * 24 * 7 });
                setUser(data.user);
                return { success: true, user: data.user, token: data.token };
            } else {
                return { success: false, error: data };
            }
        } catch (error) {
            return { success: false, error: { detail: error.message || "Network error" } };
        }
    };

    const logout = async () => {
        try {
            const response = await fetch("http://localhost:8000/api/users/logout/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Token ${cookies.auth}`
                },
                credentials: "include",
            });

            if (response.ok) {
                removeCookie('auth', { path: '/' });
                setUser(null);
                navigate('/auth');
            } else {
                console.error("Logout request failed with status:", response.status);
            }
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };


    return (
        <AuthContext.Provider value={{
            user,
            loading,
            login,
            register,
            logout,
            isAuthenticated
        }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext);