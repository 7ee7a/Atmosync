import { useState, useEffect } from 'react'

function App() {
  const [status, setStatus] = useState('Loading...');
  const [dbStatus, setDbStatus] = useState('Loading...');

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch((err) => setStatus('Error'));

    fetch('/api/db-check')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'ok') {
          setDbStatus(`PostGIS: ${data.postgis_version}`);
        } else {
          setDbStatus('Error');
        }
      })
      .catch((err) => setDbStatus('Error'));
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-text p-8 relative overflow-hidden">
      {/* Background glowing orb */}
      <div className="absolute w-[600px] h-[600px] rounded-full bg-accent opacity-10 blur-[100px] pointer-events-none -top-32 -left-32"></div>

      <div className="max-w-2xl w-full z-10 space-y-8 flex flex-col items-center">
        
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-6xl font-extrabold tracking-tight">
            AEROS<span className="text-accent">.</span>
          </h1>
          <p className="text-xl opacity-80 text-[#A0A0A0]">
            Geospatial Intelligence Platform
          </p>
        </div>

        {/* Status Dashboard */}
        <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          
          <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-2xl p-6 shadow-xl hover:border-accent/40 transition-colors duration-300">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-[#222] border border-[#333] flex items-center justify-center">
                <div className={`w-3 h-3 rounded-full ${status === 'ok' ? 'bg-accent shadow-[0_0_10px_#00FFFF]' : 'bg-red-500 shadow-[0_0_10px_red]'}`}></div>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Backend Proxy</h2>
                <p className="text-sm opacity-70 font-mono mt-1">{status === 'ok' ? '/api/health OK' : 'Offline'}</p>
              </div>
            </div>
          </div>

          <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-2xl p-6 shadow-xl hover:border-accent/40 transition-colors duration-300">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-[#222] border border-[#333] flex items-center justify-center">
                <div className={`w-3 h-3 rounded-full ${dbStatus.startsWith('PostGIS') ? 'bg-accent shadow-[0_0_10px_#00FFFF]' : 'bg-red-500 shadow-[0_0_10px_red]'}`}></div>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">PostGIS Engine</h2>
                <p className="text-sm opacity-70 text-ellipsis overflow-hidden whitespace-nowrap" title={dbStatus}>
                  {dbStatus}
                </p>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  )
}

export default App
