import React, { useEffect, useState } from 'react';
import BACKEND_URL from '../../Utils/BackendUrl';
import { Link, useNavigate } from 'react-router-dom';
import './Chats.css';

const Chats = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [chats, setChats] = useState([]);

    const handleLogout = () => {
        sessionStorage.removeItem('access_token');
        navigate('/auth');
    };

    useEffect(() => {
        const fetchUserData = async () => {
            const token = sessionStorage.getItem('access_token');
            if (!token) {
                handleLogout();
                return;
            }

            try {
                const response = await fetch(`${BACKEND_URL}/api/users/me`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.status === 401) {
                    handleLogout();
                    return;
                }

                const data = await response.json();
                setUsername(data.username);
            } catch (error) {
                console.error(error);
            }
        };

        fetchUserData();
    }, []);

    useEffect(() => {
        const fetchChats = async () => {
            const token = sessionStorage.getItem('access_token');
            if (!token) {
                handleLogout();
                return;
            }

            try {
                const response = await fetch(`${BACKEND_URL}/api/chats`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.status === 401) {
                    handleLogout();
                    return;
                }

                const usersData = await response.json();
                const formattedChats = usersData.users.map(user => ({
                    id: user.id,
                    name: `Чат с пользователем ${user.username}`,
                }));
                setChats(formattedChats);
            } catch (error) {
                console.error(error);
            }
        };

        fetchChats();
    }, [username]);

    return (
        <div className="chats-container">
            <header className="chats-header">
                <div className="header-title">
                    <h1>Чаты</h1>
                </div>
                <div className="header-right">
                    <span>{username}</span>
                    <button onClick={handleLogout}>Выйти</button>
                </div>
            </header>
            <div className="chats-content">
                <h2 className="chats-title">Список чатов</h2>
                <div className="chats-list">
                    <ul>
                        {chats.map(chat => (
                            <li key={chat.id}>
                                <Link to={`/chats/${chat.id}`} className="chat-link">
                                    {chat.name}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default Chats;
