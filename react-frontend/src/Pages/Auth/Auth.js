import React, { useState } from 'react';
import BACKEND_URL from '../../Utils/BackendUrl';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

const Auth = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const url = isRegistering
            ? `${BACKEND_URL}/api/auth/register`
            : `${BACKEND_URL}/api/auth/login`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.status === 200) {
                const data = await response.json();
                sessionStorage.setItem("access_token", data.access_token);
                navigate("/chats");
                console.log(isRegistering ? 'Успешно зарегистрирован!' : 'Успешно авторизован!', data.access_token);
            } else if (response.status === 400){
                setError('Такое имя пользователя уже занято');
            } else if (response.status === 401) {
                setError('Неверные учетные данные');
            } else {
                setError(`Ошибка: ${response.statusText}`);
            }
        } catch (error) {
            setError('Произошла ошибка при выполнении запроса');
            console.error('Ошибка:', error);
        }
    };

    return (
        <div className="container">
            <h2>{isRegistering ? 'Регистрация' : 'Авторизация'}</h2>
            <form onSubmit={handleSubmit} className="form">
                <input
                    type="text"
                    placeholder="Имя пользователя"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input"
                    required
                />
                <input
                    type="password"
                    placeholder="Пароль"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input"
                    required
                />
                <button type="submit" className="button">
                    {isRegistering ? 'Зарегистрироваться' : 'Войти'}
                </button>
                {error && <p className="error">{error}</p>}
            </form>
            <p onClick={() => setIsRegistering(!isRegistering)} className="toggle-form">
                {isRegistering ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Зарегистрироваться'}
            </p>
        </div>
    );
};

export default Auth;
