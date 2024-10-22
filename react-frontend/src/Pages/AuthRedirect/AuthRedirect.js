// src/AuthRedirect.js
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthRedirect = () => {
    const navigate = useNavigate();

    useEffect(() => {
        const token = sessionStorage.getItem('access_token');

        if (token) {
            navigate('/chats');
        } else {
            navigate('/auth');
        }
    }, [navigate]);

    return null;
};

export default AuthRedirect;
