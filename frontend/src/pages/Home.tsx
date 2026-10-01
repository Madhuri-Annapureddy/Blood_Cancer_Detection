import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  const [status, setStatus] = useState<string>('Checking backend...');

  useEffect(() => {
    axios
      .get('http://127.0.0.1:8000/health')
      .then((response) => {
        setStatus(`Backend says: ${response.data.status}`);
      })
      .catch(() => {
        setStatus('Could not reach backend. Is it running?');
      });
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Leukemia Detection Platform (Home)</h1>
      <p>{status}</p>
      
      <div style={{ marginTop: '2rem' }}>
        <h3>Navigation</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li style={{ marginBottom: '0.5rem' }}>
            <Link to="/login" style={{ color: '#3b82f6', textDecoration: 'none' }}>Go to Login</Link>
          </li>
          <li style={{ marginBottom: '0.5rem' }}>
            <Link to="/register" style={{ color: '#3b82f6', textDecoration: 'none' }}>Go to Register</Link>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Home;
