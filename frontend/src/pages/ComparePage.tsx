import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../api';
import type { AnalysisDimension } from '../context/AppContext';
import RadarChart from '../components/RadarChart';
import ScoreBar from '../components/ScoreBar';

const GITHUB_URL_RE = /^https?:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;

interface CompareResult {
  dimensions: AnalysisDimension[];
  health_score: number;
  badge_level: string;
  badge_color: string;
  repo_url: string;
}

export default function ComparePage() {
  const navigate = useNavigate();
  const [urlA, setUrlA] = useState('');
  const [urlB, setUrlB] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resultA, setResultA] = useState<CompareResult | null>(null);
  const [resultB, setResultB] = useState<CompareResult | null>(null);

  const validA = GITHUB_URL_RE.test(urlA.trim());
  const validB = GITHUB_URL_RE.test(urlB.trim());

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validA || !validB) {
      setError('两个 URL 都必须是有效的 GitHub 地址');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_a: urlA.trim(), repo_b: urlB.trim() }),
      });
      const json = await resp.json();
      if (json.code === 0) {
        setResultA(json.data.repo_a);
        setResultB(json.data.repo_b);
      } else {
        setError(json.message || '对比失败');
      }
    } catch {
      setError('网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  const hasResult = resultA && resultB;

  return (
    <div className="page-container fade-in">
      <button className="btn-back" onClick={() => navigate('/')}>&larr; 返回</button>
      <h1>仓库对比</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>输入两个 GitHub 仓库 URL，并排对比健康度</p>

      <div className="card" style={{ marginBottom: 24 }}>
        <form onSubmit={handleCompare}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 6, display: 'block' }}>仓库 A</label>
              <input
                type="text"
                placeholder="https://github.com/user/repo-a"
                value={urlA}
                onChange={(e) => { setUrlA(e.target.value); setError(''); }}
                className={`input ${urlA && !validA ? 'input-error' : ''}`}
                disabled={loading}
              />
            </div>
            <div>
              <label style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 6, display: 'block' }}>仓库 B</label>
              <input
                type="text"
                placeholder="https://github.com/user/repo-b"
                value={urlB}
                onChange={(e) => { setUrlB(e.target.value); setError(''); }}
                className={`input ${urlB && !validB ? 'input-error' : ''}`}
                disabled={loading}
              />
            </div>
          </div>

          {error && <div className="error-toast" style={{ marginBottom: 16 }}>{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', justifyContent: 'center', display: 'flex', alignItems: 'center', gap: 8 }}>
            {loading ? (<><span className="spinner-sm" />分析中...</>) : '开始对比'}
          </button>
        </form>
      </div>

      {hasResult && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            {[resultA, resultB].map((r, i) => (
              <div key={i} className="card" style={{ textAlign: 'center' }}>
                <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 8 }}>仓库 {i === 0 ? 'A' : 'B'}</p>
                <p style={{ wordBreak: 'break-all', fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>
                  {r.repo_url.replace('https://github.com/', '')}
                </p>
                <span style={{ fontSize: 32, fontWeight: 700, color: 'var(--text)' }}>{r.health_score}</span>
                <span className="badge" style={{ background: r.badge_color, marginLeft: 8, verticalAlign: 'super' }}>{r.badge_level}</span>
              </div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            {[resultA, resultB].map((r, i) => (
              <div key={i} className="card">
                <div style={{ marginBottom: 8 }}>
                  {i === 0 && r.health_score > resultB.health_score && <span className="tag" style={{ background: 'var(--green)', fontSize: 11 }}>🏆 领先</span>}
                  {i === 1 && r.health_score > resultA.health_score && <span className="tag" style={{ background: 'var(--green)', fontSize: 11 }}>🏆 领先</span>}
                </div>
                <RadarChart dimensions={(r.dimensions || []).map((d: AnalysisDimension) => ({ name: d.dimension, score: d.score }))} />
              </div>
            ))}
          </div>

          <div className="card">
            <h2 className="section-title">逐维度对比</h2>
            {resultA.dimensions.map((dA: AnalysisDimension) => {
              const dB = resultB.dimensions?.find((d: AnalysisDimension) => d.dimension === dA.dimension);
              const diff = dB ? (dA.score - dB.score) : 0;
              const aBetter = diff > 0;
              return (
                <div key={dA.dimension} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{dA.dimension}</span>
                    {diff !== 0 && (
                      <span style={{ color: aBetter ? 'var(--green)' : 'var(--red)', fontWeight: 600 }}>
                        A {aBetter ? '+' : ''}{diff.toFixed(0)}
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, alignItems: 'center' }}>
                    <div style={{ textAlign: 'right', fontSize: 13, fontWeight: 600, color: 'var(--accent)' }}>A: {dA.score}</div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>B: {dB?.score ?? '?'}</div>
                  </div>
                  <ScoreBar label="" score={Math.max(dA.score, dB?.score ?? 0)} />
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
