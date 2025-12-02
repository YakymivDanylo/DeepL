import React, {useEffect, useState} from 'react';
import {useNavigate} from "react-router-dom";
import {useAuth} from "../context/AuthContext";
import "../App.css"

const LoginPage = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const {login,isAuthenticated} = useAuth()
    const navigate = useNavigate()


    const handleSubmit= async (e) =>{
        e.preventDefault();
        setError("");

        const result = await login(username, password);

        if(result.success){
            navigate("/");
            console.log(result)
        }else{
            setError(result.error);
        }
    };

    return (
        <div className={"login-form"}>
            <h2>Login</h2>
            {error && <div className={"error-message"}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className={"form-group"}>
                    <label htmlFor="username">Username</label>
                    <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required={true}/>
                </div>
                <div className={"form-group"}>
                    <label htmlFor="password">Password</label>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required={true}/>
                </div>
                <button type={'submit'}>Login</button>
            </form>
        </div>
    )
}

export default LoginPage;