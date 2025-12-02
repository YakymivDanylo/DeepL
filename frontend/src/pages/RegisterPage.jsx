import React, {useState} from 'react';
import {useNavigate} from "react-router-dom";
import {useAuth} from "../context/AuthContext";

const RegisterPage = () =>{
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const {register} = useAuth();
    const navigate = useNavigate()

    const validateEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        return regex.test(email);
    };

    const validatePassword = (password) =>{
        const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/
        return regex.test(password);
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if(!validateEmail(email)){
            setError("Invalid email address");
            return
        }

        if (password !== confirmPassword){
            setError("Passwords do not match");
            return
        }

        if(!validatePassword(password)){
            setError("Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character")
            return
        }

        const result = await register(email, username, password, confirmPassword);

        if(result.success){
            navigate("/");
        }else{
            const err = result.error;
            if(err?.username){
                setError(`Username: ${err.username[0]}`)
            }else if(err?.email){
                setError(`Email: ${err.email[0]}`)
            }else{
                setError(err.detail || "Registration failed")
            }
        }
    };

    return (
        <div className={"register-form"}>
            <h2>Register</h2>
            {error && <div className={"error-message"}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className={"form-group"}>
                    <label htmlFor="email">Email</label>
                    <input type="email" id={"email"} value={email} required={true}
                           onChange={(e) => setEmail(e.target.value)}/>
                </div>

                <div className={"form-group"}>
                    <label htmlFor="username">Username</label>
                    <input type="text" id={"username"} value={username} required={true}
                           onChange={(e) => setUsername(e.target.value)}/>
                </div>

                <div className={"form-group"}>
                    <label htmlFor="password">Password</label>
                    <input type="password" id={"password"} value={password} required={true}
                           onChange={(e) => setPassword(e.target.value)}/>
                </div>

                <div className={"form-group"}>
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input type="password" id={"confirmPassword"} value={confirmPassword} required={true}
                           onChange={(e) => setConfirmPassword(e.target.value)}/>
                </div>

                <button type={'submit'}>Register</button>
            </form>
        </div>
    )
}

export default RegisterPage;