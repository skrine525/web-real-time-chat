import './App.css';
import Auth from './Pages/Auth/Auth';
import Chats from './Pages/Chats/Chats';
import Chat from './Pages/Chat/Chat';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import AuthRedirect from './Pages/AuthRedirect/AuthRedirect';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/auth" element={<Auth />} />
                <Route path="/chats" element={<Chats />} />
                <Route path="/chats/:userId" element={<Chat />} />
                <Route path="/" element={<AuthRedirect />} />
                <Route path="*" element={<Navigate to="/chats" />} />
            </Routes>
        </Router>
    );
}

export default App;
