import React from 'react';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';

const AuthPage = () => {
    const [isLogin, setIsLogin] = React.useState(true);

    return (
        <div className="auth-container">
            {isLogin ? <LoginPage /> : <RegisterPage />}
            <button onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Need to register?' : 'Already have an account?'}
            </button>
        </div>
    );
};

export default AuthPage;