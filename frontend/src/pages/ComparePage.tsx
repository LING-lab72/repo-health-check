import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { API_BASE } from '../api';
import type { AnalysisDimension } from '../context/AppContext';
import RadarChart from '../components/RadarChart';
import ScoreBar from '../components/ScoreBar';
import AnimatedCounter from '../components/AnimatedCounter';
import GlassCard from '../components/GlassCard';
import { downloadComparePoster } from '../utils/comparePoster';
import { normalizeBadgeColor } from '../utils/reportAssets';

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
  const [searchParams] = useSearchParams();
  const [urlA, setUrlA] = useState('');
  const [urlB, setUrlB] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resultA, setResultA] = useState<CompareResult | null>(null);
  const [resultB, setResultB] = useState<CompareResult | null>(null);

  const validA = GITHUB_URL_RE.test(urlA.trim());
  const validB = GITHUB_URL_RE.test(urlB.trim());

  useEffect(() => {
    const repoA = searchParams.get('repo_a');
    const repoB = searchParams.get('repo_b');
    if (repoA) setUrlA(repoA);
    setUrlB(repoB || '');
    setResultA(null);
    setResultB(null);
    setError('');
  }, [searchParams]);

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validA || !validB) {
      setError('两个 URL 都必须是有效的 GitHub 地址');
      return;
    }
    if (urlA.trim().replace(/\/$/, '') === urlB.trim().replace(/\/$/, '')) {
      setError('Please enter two different GitHub repositories');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_a: urlA.trim(), repo_b: urlB.trim(), skip_ai: false }),
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
  const winner = hasResult
    ? resultA.health_score >= resultB.health_score
      ? resultA
      : resultB
    : null;
  const scoreGap = hasResult ? Math.abs(resultA.health_score - resultB.health_score) : 0;

  return (
    <div className="page-container fade-in">
      <button className="btn-back" onClick={() => navigate('/')}>← 返回</button>
      <h1 className="text-gradient-purple">仓库对比</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 28 }}>输入两个 GitHub 仓库 URL，并排对比健康度</p>

      <GlassCard tilt style={{ marginBottom: 28 }}>
        <form onSubmit={handleCompare}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6, display: 'block' }}>仓库 A</label>
              <input
                type="text"
                placeholder="https://github.com/user/repo-a"
                value={urlA}
                onChange={(e) => { setUrlA(e.target.value); setError(''); }}
                className={`input ${urlA && !validA ? 'input-error' : ''}`}
                disabled={loading}
                autoComplete="off"
              />
            </div>
            <div>
              <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6, display: 'block' }}>仓库 B</label>
              <input
                type="text"
                placeholder="https://github.com/user/repo-b"
                value={urlB}
                onChange={(e) => { setUrlB(e.target.value); setError(''); }}
                className={`input ${urlB && !validB ? 'input-error' : ''}`}
                disabled={loading}
                autoComplete="off"
              />
            </div>
          </div>

          {error && <div className="error-toast" style={{ marginBottom: 16 }}>{error}</div>}

          <button type="submit" className="btn" disabled={loading} style={{ width: '100%', justifyContent: 'center', display: 'flex', alignItems: 'center', gap: 8 }}>
            {loading ? (<><span className="spinner-sm" />分析中...</>) : '开始对比'}
          </button>
        </form>
      </GlassCard>

      {hasResult && (
        <>
          {/* Score Comparison */}
          <div className="compare-score-grid">
            {[resultA, resultB].map((r, i) => (
              <GlassCard key={i} tilt style={{ textAlign: 'center' }}>
                <p style={{ color: 'var(--text-secondary)', fontSize: 13, fontWeight: 600, marginBottom: 8 }}>仓库 {i === 0 ? 'A' : 'B'}</p>
                <p style={{ wordBreak: 'break-all', fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>
                  {r.repo_url.replace('https://github.com/', '')}
                </p>
                <span className="score-number text-gradient">
                  <AnimatedCounter target={r.health_score} />
                </span>
                <span className="score-label" style={{ marginLeft: 4 }}>/100</span>
                <span className="badge" style={{ background: r.badge_color, marginLeft: 12, marginTop: 8, display: 'inline-block' }}>{r.badge_level}</span>
              </GlassCard>
            ))}
            {/* VS divider in middle column */}
            <div className="vs-divider">VS</div>
          </div>

          <GlassCard style={{ marginBottom: 28 }}>
            <div className="pk-arena">
              <div className="pk-header">
                <span>Repository PK Arena</span>
                <strong>{winner?.repo_url.replace(/^https?:\/\/github\.com\//, '')} wins</strong>
                <em>领先 {scoreGap.toFixed(0)} 分</em>
              </div>
              <div className="pk-board">
                {[resultA, resultB].map((r, i) => {
                  const isWinner = winner?.repo_url === r.repo_url;
                  const energy = Math.max(4, Math.min(100, r.health_score));
                  return (
                    <div key={r.repo_url} className={`pk-fighter ${isWinner ? 'winner' : ''}`}>
                      <div className="pk-avatar" style={{ borderColor: normalizeBadgeColor(r.badge_color) }}>
                        {i === 0 ? 'A' : 'B'}
                      </div>
                      <div className="pk-meta">
                        <strong>{r.repo_url.replace(/^https?:\/\/github\.com\//, '')}</strong>
                        <span>{Math.round(r.health_score)} / 100</span>
                      </div>
                      <div className="pk-health">
                        <div
                          style={{
                            width: `${energy}%`,
                            background: normalizeBadgeColor(r.badge_color),
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
              <button
                className="btn btn-sm"
                onClick={() => downloadComparePoster(resultA, resultB)}
                style={{ marginTop: 18 }}
              >
                生成 PK 海报
              </button>
            </div>
          </GlassCard>

          {/* Radar Charts */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 28 }}>
            {[resultA, resultB].map((r, i) => (
              <GlassCard key={i}>
                <div style={{ marginBottom: 8 }}>
                  {i === 0 && r.health_score > resultB.health_score && <span className="tag" style={{ background: 'var(--accent-secondary)', fontSize: 11 }}>领先</span>}
                  {i === 1 && r.health_score > resultA.health_score && <span className="tag" style={{ background: 'var(--accent-secondary)', fontSize: 11 }}>领先</span>}
                </div>
                <RadarChart dimensions={(r.dimensions || []).map((d: AnalysisDimension) => ({ name: d.dimension, score: d.score }))} />
              </GlassCard>
            ))}
          </div>

          {/* Dimension Comparison */}
          <GlassCard>
            <h2 className="section-title text-gradient-purple">逐维度对比</h2>
            {resultA.dimensions.map((dA: AnalysisDimension) => {
              const dB = resultB.dimensions?.find((d: AnalysisDimension) => d.dimension === dA.dimension);
              const diff = dB ? (dA.score - dB.score) : 0;
              const aBetter = diff > 0;
              return (
                <div key={dA.dimension} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                    <span style={{ fontWeight: 600 }}>{dA.dimension}</span>
                    {diff !== 0 && (
                      <span style={{ color: aBetter ? 'var(--accent-secondary)' : 'var(--red)', fontWeight: 700, fontSize: 12 }}>
                        A {aBetter ? '+' : ''}{diff.toFixed(0)}
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <span style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 600 }}>A: {dA.score}</span>
                      <ScoreBar label="" score={dA.score} />
                    </div>
                    <div>
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>B: {dB?.score ?? '?'}</span>
                      <ScoreBar label="" score={dB?.score ?? 0} />
                    </div>
                  </div>
                </div>
              );
            })}
          </GlassCard>
        </>
      )}
    </div>
  );
}
