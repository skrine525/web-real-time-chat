import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import BACKEND_URL from '../../Utils/BackendUrl';
import './Chat.css';

const Chat = () => {
    const navigate = useNavigate();
    const socket = useRef(null);
    const receiverUsername = useRef('');
    const { userId } = useParams();
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [username, setUsername] = useState('');
    const [chatName, setChatName] = useState('');

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
        const fetchMessages = async () => {
            const token = sessionStorage.getItem('access_token');
            if (!token) {
                handleLogout();
                return;
            }

            try {
                const response = await fetch(`${BACKEND_URL}/api/chats/${userId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setChatName(`Чат с ${data.user.username}`);
                    receiverUsername.current = data.user.username;

                    const messages = [];
                    data.messages.map((value) => {
                        messages.push({
                            sender: value.type === "sent" ? username : receiverUsername.current,
                            text: value.text
                        });
                    });

                    setMessages(messages);
                }
            } catch (error) {
                console.error(error);
            }
        };

        fetchMessages();
    }, [username]);

    useEffect(() => {
        const token = sessionStorage.getItem('access_token');
        if (!token || socket.current || !username) return;

        // Подключаемся к WebSocket с передачей userId и access_token в строке запроса
        socket.current = new WebSocket(
            `${BACKEND_URL.replace('http', 'ws')}/api/chats/${userId}/ws?access_token=${token}`
        );

        // Обработчик получения сообщений
        socket.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log(message);

            if (message.type === 'joined') {
                const newMessage = {
                    sender: message.sender,
                    text: message.sender === username ? '[Вы присоединились к чату]' : '[Собеседник присоединился к чату]'
                };
                // setMessages((prevMessages) => [...prevMessages, newMessage]);
            }
            else if (message.type === 'left') {
                const newMessage = {
                    sender: message.sender,
                    text: '[Собеседник покинул чат]'
                };
                // setMessages((prevMessages) => [...prevMessages, newMessage]);
            }
            else if (message.type === 'new_message') {
                const newMessage = {
                    sender: message.sender,
                    text: message.payload.text
                };
                setMessages((prevMessages) => [...prevMessages, newMessage]);
            }
        };

        // Обработчик ошибок
        socket.current.onerror = (error) => {
            console.error('WebSocket Error:', error);
        };

        // Закрытие соединения при размонтировании компонента
        return () => {
            if (socket.current) {
                socket.current.close();
                socket.current = null;
            }
        };
    }, [username]);

    const handleSendMessage = async () => {
        if (!newMessage.trim()) return;

        const event = {
            type: 'new_message',
            sender: username,
            receiver: receiverUsername.current,
            payload: {
                text: newMessage
            }
        };

        // Отправка сообщения через WebSocket
        if (socket.current && socket.current.readyState === WebSocket.OPEN) {
            socket.current.send(JSON.stringify(event));
            setNewMessage(''); // Очистить поле ввода
        } else {
            console.error('WebSocket is not open.');
        }
    };

    const handleKeyUp = (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div className="chat-container">
            <header className="chat-header">
                <div className="header-title">
                    <h1>{chatName}</h1>
                </div>
                <div className="header-right">
                    <span>{username}</span>
                    <button onClick={handleLogout}>Выйти</button>
                </div>
            </header>
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender === username ? 'sent' : 'received'}`}>
                        <strong>{msg.sender}: </strong>{msg.text}
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyUp={handleKeyUp}
                    placeholder="Введите сообщение..."
                />
                <button onClick={handleSendMessage}>Отправить</button>
            </div>
        </div>
    );
};

export default Chat;
