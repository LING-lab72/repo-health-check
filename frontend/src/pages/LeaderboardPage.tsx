import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../api';
import AnimatedCounter from '../components/AnimatedCounter';

interface LeaderboardItem {
  repo_url: string;
  health_score: number;
  badge_level: string;
  badge_color: string;
  analyzed_at: string;
  _votes?: number;
  _trend?: 'up' | 'down' | 'same' | 'new';
}

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
    if (votingRepo) return;
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
    <div className="page-container fade-in stagger-children">
      <button className="btn-back" onClick={() => navigate('/')}>← 返回</button>

      <h1 className="text-gradient-purple">仓库健康排行榜</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 28 }}>
        已分析 {items.length} 个仓库
      </p>

      {voteError && (
        <div className="error-toast" style={{ marginBottom: 16 }}>{voteError}</div>
      )}

      {/* Weekly Best */}
      {topRepo && (
        <div className="lb-week-best" style={{ marginBottom: 28 }}>
          <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent)', letterSpacing: '0.03em' }}>本周最健康仓库</span>
          <p style={{ fontSize: 16, fontWeight: 700, marginTop: 6, wordBreak: 'break-all' }}>
            {topRepo.repo_url.replace('https://github.com/', '')}
          </p>
          <div style={{ marginTop: 8 }}>
            <span className="score-number text-gradient">
              <AnimatedCounter target={topRepo.health_score} />
            </span>
            <span className="score-label" style={{ marginLeft: 4 }}>/100</span>
            <span className="badge" style={{ background: topRepo.badge_color, marginLeft: 12 }}>
              {topRepo.badge_level}
            </span>
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: 48 }}>
          <p style={{ fontSize: 48, marginBottom: 16 }}>📭</p>
          <p style={{ color: 'var(--text-secondary)' }}>暂无排行数据，去首页分析第一个仓库吧</p>
        </div>
      ) : (
        <div>
          {/* Header row */}
          <div className="lb-row" style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, marginBottom: 8, border: 'none', background: 'transparent', backdropFilter: 'none' }}>
            <span style={{ width: 48 }}>排名</span>
            <span style={{ flex: 1 }}>仓库</span>
            <span style={{ width: 60, textAlign: 'right' }}>分数</span>
            <span style={{ width: 35, textAlign: 'center' }}>趋势</span>
            <span style={{ width: 60, textAlign: 'center' }}>等级</span>
            <span style={{ width: 60, textAlign: 'center' }}>投票</span>
          </div>

          {/* Leader rows */}
          {items.map((item, i) => {
            const rank = i + 1;
            const repoName = item.repo_url.replace(/^https?:\/\/github\.com\//, '');
            const votes = item._votes || 0;
            const rankClass = rank <= 3 ? `lb-rank-${rank}` : 'lb-rank-default';

            return (
              <div key={item.repo_url} className="lb-row">
                <div className={`lb-rank-badge ${rankClass}`}>
                  {rank}
                </div>
                <span style={{ flex: 1, fontSize: 14, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={repoName}>
                  {repoName}
                </span>
                <span style={{ width: 60, textAlign: 'right', fontWeight: 800, fontSize: 14, fontVariantNumeric: 'tabular-nums', color: 'var(--text)' }}>
                  {item.health_score}
                </span>
                <span style={{ width: 35, textAlign: 'center', fontSize: 14 }}>
                  {item._trend === 'up' && <span style={{ color: 'var(--green)' }}>↑</span>}
                  {item._trend === 'down' && <span style={{ color: 'var(--red)' }}>↓</span>}
                  {item._trend === 'new' && <span style={{ color: 'var(--blue)', fontSize: 10, fontWeight: 700, letterSpacing: '0.05em' }}>NEW</span>}
                  {item._trend === 'same' && <span style={{ color: 'var(--text-secondary)' }}>—</span>}
                </span>
                <span style={{ width: 60, textAlign: 'center' }}>
                  <span className="badge" style={{ background: item.badge_color, fontSize: 12, padding: '2px 8px' }}>
                    {item.badge_level}
                  </span>
                </span>
                <span style={{ width: 60, textAlign: 'center' }}>
                  <button
                    onClick={() => handleVote(item.repo_url)}
                    disabled={votingRepo === item.repo_url}
                    style={{
                      background: 'none',
                      border: '1px solid var(--border)',
                      opacity: votingRepo === item.repo_url ? 0.4 : 1,
                      cursor: 'pointer',
                      fontSize: 13,
                      padding: '4px 10px',
                      borderRadius: 8,
                      transition: 'all 0.2s',
                      color: 'var(--text-secondary)',
                    }}
                    title="点赞"
                  >
                    👍 {votes}
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
