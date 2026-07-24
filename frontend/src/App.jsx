import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Flag, Settings, Loader2, Play } from 'lucide-react';
import TelemetryChart from './components/TelemetryChart';
import RacePaceChart from './components/RacePaceChart';

import { getDriverColor } from './utils/colors';

const API_BASE = 'http://localhost:8000/api/analysis';

function App() {
  const [activeTab, setActiveTab] = useState('fastest');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [racePaceData, setRacePaceData] = useState(null);
  
  const [params, setParams] = useState({
    year: '2024',
    event: 'Bahrain',
    session_type: 'Q',
    drivers: 'VER,LEC'
  });

  const handleParamChange = (e) => {
    setParams({
      ...params,
      [e.target.name]: e.target.value
    });
  };

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'fastest') {
        const res = await axios.get(`${API_BASE}/fastest`, { params });
        setData(res.data);
      } else {
        const res = await axios.get(`${API_BASE}/race-pace`, { 
          params: { ...params, session_type: 'R' } 
        });
        setRacePaceData(res.data);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to load data. See console for details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'race-pace') {
      setParams(p => ({ ...p, session_type: 'R' }));
    }
  }, [activeTab]);

  return (
    <div className="app-container">
      <header>
        <div className="logo">
          <Activity className="logo-icon" size={32} />
          F1 Data Dynamics
        </div>
        <div>
          <button className="primary-btn" onClick={loadData} disabled={loading}>
            {loading ? <Loader2 className="spinner" size={20} /> : <Play size={20} />}
            {loading ? 'Analyzing...' : 'Load Analysis'}
          </button>
        </div>
      </header>

      <div className="glass-panel" style={{ marginBottom: '2rem' }}>
        <div className="controls-grid">
          <div className="input-group">
            <label>Season</label>
            <input name="year" value={params.year} onChange={handleParamChange} />
          </div>
          <div className="input-group">
            <label>Grand Prix</label>
            <select name="event" value={params.event} onChange={handleParamChange}>
              <option value="Bahrain Grand Prix">Bahrain Grand Prix</option>
              <option value="Saudi Arabian Grand Prix">Saudi Arabian Grand Prix</option>
              <option value="Australian Grand Prix">Australian Grand Prix</option>
              <option value="Japanese Grand Prix">Japanese Grand Prix</option>
              <option value="Chinese Grand Prix">Chinese Grand Prix</option>
              <option value="Miami Grand Prix">Miami Grand Prix</option>
              <option value="Emilia Romagna Grand Prix">Emilia Romagna Grand Prix</option>
              <option value="Monaco Grand Prix">Monaco Grand Prix</option>
              <option value="Canadian Grand Prix">Canadian Grand Prix</option>
              <option value="Spanish Grand Prix">Spanish Grand Prix</option>
              <option value="Austrian Grand Prix">Austrian Grand Prix</option>
              <option value="British Grand Prix">British Grand Prix</option>
              <option value="Hungarian Grand Prix">Hungarian Grand Prix</option>
              <option value="Belgian Grand Prix">Belgian Grand Prix</option>
              <option value="Dutch Grand Prix">Dutch Grand Prix</option>
              <option value="Italian Grand Prix">Italian Grand Prix</option>
              <option value="Azerbaijan Grand Prix">Azerbaijan Grand Prix</option>
              <option value="Singapore Grand Prix">Singapore Grand Prix</option>
              <option value="United States Grand Prix">United States Grand Prix</option>
              <option value="Mexico City Grand Prix">Mexico City Grand Prix</option>
              <option value="São Paulo Grand Prix">São Paulo Grand Prix</option>
              <option value="Las Vegas Grand Prix">Las Vegas Grand Prix</option>
              <option value="Qatar Grand Prix">Qatar Grand Prix</option>
              <option value="Abu Dhabi Grand Prix">Abu Dhabi Grand Prix</option>
            </select>
          </div>
          <div className="input-group">
            <label>Session</label>
            <select name="session_type" value={params.session_type} onChange={handleParamChange} disabled={activeTab === 'race-pace'}>
              <option value="Q">Qualifying</option>
              <option value="R">Race</option>
              <option value="Sprint">Sprint</option>
              <option value="FP1">Practice 1</option>
              <option value="FP2">Practice 2</option>
              <option value="FP3">Practice 3</option>
            </select>
          </div>
          <div className="input-group">
            <label>Drivers (Comma separated)</label>
            <input name="drivers" value={params.drivers} onChange={handleParamChange} />
          </div>
        </div>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'fastest' ? 'active' : ''}`}
          onClick={() => setActiveTab('fastest')}
        >
          <Activity size={18} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }} />
          Qualifying / Fastest Lap
        </button>
        <button 
          className={`tab ${activeTab === 'race-pace' ? 'active' : ''}`}
          onClick={() => setActiveTab('race-pace')}
        >
          <Flag size={18} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }} />
          Race Pace Analysis
        </button>
      </div>

      {loading && (
        <div className="glass-panel loader">
          <Loader2 size={48} className="spinner" />
          <p>Fetching and processing telemetry data...</p>
        </div>
      )}

      {!loading && activeTab === 'fastest' && data && (
        <div className="dashboard-grid two-cols">
          <div className="glass-panel" style={{ overflowX: 'hidden' }}>
            <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              Telemetry Comparison
            </h3>
            <TelemetryChart telemetryData={data.telemetry} corners={data.corners} />
          </div>
          
          <div className="glass-panel">
            <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              Lap Summary
            </h3>
            <div className="summary-cards">
              {data.summary.map((driverData, idx) => (
                <div 
                  key={driverData.Driver} 
                  className="driver-card glass-panel"
                  style={{ 
                    '--driver-color': getDriverColor(driverData.Driver),
                    padding: '1rem',
                    marginBottom: '1rem',
                    boxShadow: 'none',
                    background: 'rgba(0,0,0,0.2)'
                  }}
                >
                  <div className="driver-header">
                    <div className="driver-name">{driverData.Driver}</div>
                    <div className="driver-laptime">
                      {driverData.DeltaToRef === 0 || idx === 0 
                        ? `${(driverData.LapTime / 60).toFixed(0)}:${(driverData.LapTime % 60).toFixed(3).padStart(6, '0')}` 
                        : `+${driverData.DeltaToRef.toFixed(3)}s`}
                    </div>
                  </div>
                  <div className="stat-grid">
                    <div className="stat-item">
                      <span className="stat-label">Compound</span>
                      <span className="stat-value">{driverData.Compound} (L{driverData.TyreLife})</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Top Speed</span>
                      <span className="stat-value">{driverData.TopSpeed} km/h</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Full Throttle</span>
                      <span className="stat-value">{driverData.FullThrottle}%</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Avg Speed</span>
                      <span className="stat-value">{driverData.AvgSpeed.toFixed(1)} km/h</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {!loading && activeTab === 'race-pace' && racePaceData && (
        <div className="dashboard-grid">
          <div className="glass-panel">
            <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              Long Run Pace & Tyre Degradation
            </h3>
            <RacePaceChart paceData={racePaceData.race_pace} />
          </div>
        </div>
      )}
      
      {!loading && !data && activeTab === 'fastest' && (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
          <Settings size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
          <h2>Ready to Analyze</h2>
          <p>Configure parameters and click Load Analysis to start.</p>
        </div>
      )}
    </div>
  );
}

export default App;
