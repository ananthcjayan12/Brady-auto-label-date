import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Printer, CheckCircle, AlertCircle, RefreshCw, Settings, LayoutDashboard } from 'lucide-react';
import LabelDashboard from './components/LabelDashboard';
import './App.css';

const API_BASE_URL = 'http://localhost:5001';

function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState('dashboard');

  // App State
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState({ type: 'idle', message: 'Ready' });
  const [printers, setPrinters] = useState([]);
  const [selectedPrinter, setSelectedPrinter] = useState('');

  // Label Settings
  const [labelSettings, setLabelSettings] = useState(() => {
    const saved = localStorage.getItem('labelSettings');
    return saved ? JSON.parse(saved) : {
      labelWidth: 50,
      labelHeight: 25,
      fontSize: 8,
      qrSize: 15
    };
  });

  // Sync settings to localStorage
  useEffect(() => {
    localStorage.setItem('labelSettings', JSON.stringify(labelSettings));
  }, [labelSettings]);

  // Fetch available printers on mount
  useEffect(() => {
    const fetchPrinters = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/printers`);
        setPrinters(response.data.printers || []);
        setSelectedPrinter(response.data.default || '');
      } catch (error) {
        console.error('Failed to fetch printers:', error);
        setStatus({ type: 'error', message: 'Backend unreachable. Check server.' });
      }
    };
    fetchPrinters();
  }, []);

  return (
    <div className={`app-container ${status.type}`}>
      <header className="app-header">
        <div className="logo-section">
          <h1>Brady Auto Label System</h1>
          <span className="version">v1.0</span>
        </div>

        <div className="printer-selector">
          <Printer size={18} />
          <select
            value={selectedPrinter}
            onChange={(e) => setSelectedPrinter(e.target.value)}
            disabled={isLoading}
          >
            {printers.length === 0 && <option>No printers found</option>}
            {printers.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
      </header>

      <main className="app-main">
        <nav className="tab-nav">
          <button
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} style={{ marginRight: '8px' }} />
            Dashboard
          </button>
          <button
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <Settings size={18} style={{ marginRight: '8px' }} />
            Settings
          </button>
        </nav>

        {activeTab === 'dashboard' ? (
          <div className="dashboard-content">
            <div className="status-banner" style={{ margin: '1rem 2rem 0' }}>
              {status.type === 'success' && <CheckCircle className="icon" />}
              {status.type === 'error' && <AlertCircle className="icon" />}
              {status.type === 'loading' && <RefreshCw className="icon spinning" />}
              <p>{status.message}</p>
            </div>

            <LabelDashboard
              apiBaseUrl={API_BASE_URL}
              onStatusChange={setStatus}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
              selectedPrinter={selectedPrinter}
              labelSettings={labelSettings}
            />
          </div>
        ) : (
          <div className="settings-container">
            <h2>Label Layout Settings</h2>
            <div className="label-settings-grid">
              <div className="setting-item">
                <label>Label Width (mm)</label>
                <div className="slider-box">
                  <input
                    type="range" min="30" max="100" step="1"
                    value={labelSettings.labelWidth}
                    onChange={(e) => setLabelSettings({ ...labelSettings, labelWidth: parseInt(e.target.value) })}
                  />
                  <span className="setting-val">{labelSettings.labelWidth}mm</span>
                </div>
              </div>

              <div className="setting-item">
                <label>Label Height (mm)</label>
                <div className="slider-box">
                  <input
                    type="range" min="15" max="60" step="1"
                    value={labelSettings.labelHeight}
                    onChange={(e) => setLabelSettings({ ...labelSettings, labelHeight: parseInt(e.target.value) })}
                  />
                  <span className="setting-val">{labelSettings.labelHeight}mm</span>
                </div>
              </div>

              <div className="setting-item">
                <label>QR Code Size (mm)</label>
                <div className="slider-box">
                  <input
                    type="range" min="10" max="30" step="1"
                    value={labelSettings.qrSize}
                    onChange={(e) => setLabelSettings({ ...labelSettings, qrSize: parseInt(e.target.value) })}
                  />
                  <span className="setting-val">{labelSettings.qrSize}mm</span>
                </div>
              </div>

              <div className="setting-item">
                <label>Font Size (pt)</label>
                <div className="slider-box">
                  <input
                    type="range" min="6" max="14" step="0.5"
                    value={labelSettings.fontSize}
                    onChange={(e) => setLabelSettings({ ...labelSettings, fontSize: parseFloat(e.target.value) })}
                  />
                  <span className="setting-val">{labelSettings.fontSize}pt</span>
                </div>
              </div>

              <div style={{ marginTop: '20px' }}>
                <button
                  className="reset-btn"
                  onClick={() => setLabelSettings({
                    labelWidth: 50,
                    labelHeight: 25,
                    fontSize: 8,
                    qrSize: 15
                  })}
                >
                  Reset to Defaults
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Brady Auto Label System - Tracking & Generation</p>
      </footer>
    </div>
  );
}

export default App;

