import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home/Home';
import ClientPage from './pages/ClientPage/ClientPage';
import PromptEditor from './pages/PromptEditor/PromptEditor';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/client/:clientId" element={<ClientPage />} />
        <Route path="/prompts" element={<PromptEditor />} />
      </Routes>
    </Router>
  );
}

export default App;

