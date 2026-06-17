import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../api';

interface LeaderboardItem {
  repo_url: string;
  health_score: number;
  badge_level: string;
  badge_color: string;
  analyzed_at: string;
  _votes?: number;
  _trend?: 'up' | 'down' | 'same' | 'new';
}

const MEDALS: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };

export default function LeaderboardPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLeaderboard = () => {
    fetch(`${API_BASE}/api/leaderboard`)
      .then((r) => r.json())
      .then((json) => setItems(json.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchLeaderboard(); }, []);

  const [voteError, setVoteError] = useState('');
  const [votingRepo, setVotingRepo] = useState<string | null>(null);

  const handleVote = async (repoUrl: string) => {
    if (votingRepo) return; // prevent double click
    setVoteError('');
    setVotingRepo(repoUrl);
    try {
      const resp = await fetch(`${API_BASE}/api/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl }),
      });
      if (resp.status === 429) {
        setVoteError('投票太频繁，请稍后再试');
        setTimeout(() => setVoteError(''), 3000);
        return;
      }
      fetchLeaderboard();
    } finally {
      setVotingRepo(null);
    }
  };

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: 80 }}>
        <div className="spinner" />
      </div>
    );
  }

  const topRepo = items[0] as LeaderboardItem | undefined;

  return (
    <div className="page-container fade-in">
      <button className="btn-back" onClick={() => navigate('/')}>&larr; 返回</button>

      <h1>仓库健康排行榜</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
        已分析 {items.length} 个仓库
      </p>

      {voteError && (
        <div className="error-toast" style={{ marginBottom: 16 }}>{voteError}</div>
      )}

      {/* Weekly Challenge */}
      {topRepo && (
        <div className="card" style={{ marginBottom: 24, background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,122,250,0.1))', border: '1px solid rgba(99,102,241,0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--accent)' }}>🏆 本周最健康仓库</span>
              <p style={{ fontSize: 16, fontWeight: 700, marginTop: 4, wordBreak: 'break-all' }}>
                {topRepo.repo_url.replace('https://github.com/', '')}
              </p>
            </div>
            <span style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent)' }}>
              {topRepo.health_score}/100
              <span className="badge" style={{ background: topRepo.badge_color, marginLeft: 8, verticalAlign: 'super' }}>
                {topRepo.badge_level}
              </span>
            </span>
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
          <p style={{ fontSize: 48, marginBottom: 16 }}>📭</p>
          <p style={{ color: 'var(--text-secondary)' }}>暂无排行数据，去首页分析第一个仓库吧</p>
        </div>
      ) : (
        <div className="card" style={{ overflow: 'hidden' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '50px 1fr 60px 35px 60px 60px',
              padding: '12px 16px',
              borderBottom: '1px solid var(--border)',
              color: 'var(--text-secondary)',
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            <span>排名</span>
            <span>仓库</span>
            <span style={{ textAlign: 'right' }}>分数</span>
            <span style={{ textAlign: 'center' }}>趋势</span>
            <span style={{ textAlign: 'center' }}>等级</span>
            <span style={{ textAlign: 'center' }}>👍</span>
          </div>
          {items.map((item, i) => {
            const rank = i + 1;
            const repoName = item.repo_url.replace(/^https?:\/\/github\.com\//, '');
            const votes = item._votes || 0;

            return (
              <div
                key={item.repo_url}
                className="card-hover"
                style={{
                  display: 'grid',
                  gridTemplateColumns: '50px 1fr 60px 35px 60px 60px',
                  padding: '14px 16px',
                  borderBottom: i < items.length - 1 ? '1px solid var(--border)' : 'none',
                  alignItems: 'center',
                }}
              >
                <span style={{
                  fontSize: 18, fontWeight: 700,
                  color: rank <= 3 ? 'var(--accent)' : 'var(--text-secondary)',
                }}>
                  {MEDALS[rank] || rank}
                </span>
                <span style={{ fontSize: 14, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={repoName}>
                  {repoName}
                </span>
                <span style={{ textAlign: 'right', fontWeight: 700, color: 'var(--text)' }}>
                  {item.health_score}
                </span>
                <span style={{ textAlign: 'center', fontSize: 13 }}>
                  {item._trend === 'up' && <span style={{ color: 'var(--green)' }}>↑</span>}
                  {item._trend === 'down' && <span style={{ color: 'var(--red)' }}>↓</span>}
                  {item._trend === 'new' && <span style={{ color: 'var(--blue)', fontSize: 10, fontWeight: 600 }}>NEW</span>}
                  {item._trend === 'same' && <span style={{ color: 'var(--text-secondary)' }}>—</span>}
                </span>
                <span style={{ textAlign: 'center' }}>
                  <span className="badge" style={{ background: item.badge_color, fontSize: 12, padding: '2px 8px' }}>
                    {item.badge_level}
                  </span>
                </span>
                <span style={{ textAlign: 'center' }}>
                  <button
                    onClick={() => handleVote(item.repo_url)}
                    disabled={votingRepo === item.repo_url}
                    style={{
                      background: 'none',
                      border: 'none',
                      opacity: votingRepo === item.repo_url ? 0.4 : 1,
                      cursor: 'pointer',
                      fontSize: 16,
                      padding: '4px 8px',
                      borderRadius: 6,
                      transition: 'background 0.2s',
                    }}
                    title="点赞"
                  >
                    👍 <span style={{ fontSize: 12, color: 'var(--text-secondary)', marginLeft: 2 }}>{votes}</span>
                  </button>
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
