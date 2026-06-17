import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import RadarChart from '../components/RadarChart';
import ScoreBar from '../components/ScoreBar';
import HistoryChart from '../components/HistoryChart';
import AnimatedCounter from '../components/AnimatedCounter';
import GlassCard from '../components/GlassCard';
import { API_BASE, sha256Prefix, getApiKey } from '../api';

const SEVERITY_COLORS: Record<string, string> = {
  high: 'var(--red)',
  medium: 'var(--yellow)',
  low: 'var(--blue)',
};

export default function ReportPage() {
  const { repoId } = useParams<{ repoId: string }>();
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const repoUrl = repoId ? decodeURIComponent(repoId) : '';

  const [copied, setCopied] = useState(false);
  const [shareCopied, setShareCopied] = useState(false);
  const [history, setHistory] = useState<
    Array<{ analyzed_at: string; health_score: number; badge_level: string }>
  >([]);
  const [badgeHash, setBadgeHash] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  // ── Primary analysis trigger ──

  useEffect(() => {
    if (!repoUrl) return;

    dispatch({ type: 'RESET' });

    const run = async () => {
      dispatch({ type: 'START_ANALYSIS' });

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000);

      const hasKey = !!getApiKey();

      try {
        const resp = await fetch(`${API_BASE}/api/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({
            repo_url: repoUrl,
            force_sync: true,
            skip_ai: !hasKey,
          }),
        });
        clearTimeout(timeoutId);
        const json = await resp.json();

        if (json.code === 0 && json.data) {
          dispatch({ type: 'ANALYSIS_SUCCESS', payload: json.data });
        } else if (json.code === -1) {
          dispatch({ type: 'ANALYSIS_ERROR', payload: json.message || '分析失败' });
        } else {
          dispatch({ type: 'ANALYSIS_ERROR', payload: json.message || '请求失败' });
        }
      } catch (err: unknown) {
        clearTimeout(timeoutId);
        if (err instanceof DOMException && err.name === 'AbortError') {
          dispatch({ type: 'ANALYSIS_ERROR', payload: '分析超时（超过 3 分钟），仓库可能过大，请尝试较小的仓库' });
        } else {
          dispatch({ type: 'ANALYSIS_ERROR', payload: '无法连接后端服务' });
        }
      }
    };

    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repoUrl]);

  // ── Fetch AI diagnosis on demand ──

  const handleFetchDiagnosis = async () => {
    setAiLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, force_sync: true, skip_ai: false }),
      });
      const json = await resp.json();
      if (json.code === 0 && json.data) {
        dispatch({ type: 'ANALYSIS_SUCCESS', payload: json.data });
      }
    } catch {
      // silent fail
    }
    setAiLoading(false);
  };

  // ── History ──

  useEffect(() => {
    if (!repoUrl || state.status !== 'success') return;
    fetch(`${API_BASE}/api/history/${encodeURIComponent(repoUrl)}`)
      .then((r) => r.json())
      .then((json) => setHistory(json.data || []))
      .catch(() => {});
  }, [repoUrl, state.status]);

  // ── Badge hash ──

  useEffect(() => {
    if (repoUrl) {
      sha256Prefix(repoUrl).then(setBadgeHash);
    }
  }, [repoUrl]);

  const badgeMd = `![health](/api/badge/${badgeHash})`;
  const badgeImgUrl = `${API_BASE}/api/badge/${badgeHash}`;

  const copyBadge = () => {
    navigator.clipboard.writeText(badgeMd).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // ── Loading ──

  if (state.status === 'loading') {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: 80 }}>
        <div className="spinner" />
        <p style={{ marginTop: 16, color: 'var(--text-secondary)' }}>
          正在克隆并分析 {repoUrl}，通常需要 30-120 秒...
        </p>
      </div>
    );
  }

  // ── Error ──

  if (state.status === 'error') {
    const errMsg = state.error || '未知错误';
    return (
      <div className="page-container fade-in">
        <button className="btn-back" onClick={() => navigate('/')}>← 返回</button>
        <GlassCard style={{ textAlign: 'center', padding: 48, marginTop: 24 }}>
          <p style={{ color: 'var(--red)', fontSize: 18, fontWeight: 700, marginBottom: 12 }}>分析失败</p>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 16 }}>{errMsg}</p>
          <button className="btn" onClick={() => navigate('/')}>重新分析</button>
        </GlassCard>
      </div>
    );
  }

  // ── Data ready ──

  const data = state.analysisResult;
  if (!data) return null;

  const dimensions = data.dimensions || [];
  const radarData = dimensions.map((d: { dimension: string; score: number }) => ({
    name: d.dimension,
    score: d.score,
  }));
  const diagnosis = data.ai_diagnosis || [];
  const allIssues = dimensions.flatMap((d: { dimension: string; issues: string[] }) =>
    (d.issues || []).map((i: string) => `[${d.dimension}] ${i}`)
  );

  return (
    <div className="page-container fade-in stagger-children">
      <button className="btn-back" onClick={() => navigate('/')}>← 返回</button>

      {/* Header with animated score */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 20, flexWrap: 'wrap', marginBottom: 8 }}>
        <h1 className="text-gradient-purple">体检报告</h1>
        <span className="badge-glow" style={{ background: data.badge_color === 'lightgrey' ? '#9f9f9f' : data.badge_color }}>
          {data.badge_level}
        </span>
        <span className="score-number text-gradient">
          <AnimatedCounter target={data.health_score} decimals={0} />
        </span>
        <span className="score-label">/100</span>
        <button
          onClick={() => {
            const link = document.createElement('a');
            link.href = `${API_BASE}/api/export/${badgeHash}`;
            link.download = `repo-health-report-${repoUrl.replace('https://github.com/', '').replace('/', '-')}.html`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }}
          className="btn btn-sm"
          style={{ marginLeft: 'auto' }}
        >
          导出报告
        </button>
      </div>
      <p className="repo-url">{repoUrl}</p>

      {/* Radar Chart */}
      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">六维度雷达图</h2>
        <RadarChart dimensions={radarData} />
      </GlassCard>

      {/* Score Bars */}
      {dimensions.length > 0 && (
        <GlassCard style={{ marginBottom: 28 }}>
          <h2 className="section-title">各维度详情</h2>
          {dimensions.map((d: { dimension: string; score: number }) => (
            <ScoreBar key={d.dimension} label={d.dimension} score={d.score} />
          ))}
        </GlassCard>
      )}

      {/* History Chart */}
      {history.length >= 2 && <HistoryChart history={history} />}

      {/* AI Diagnosis */}
      {diagnosis.length === 0 && (
        <GlassCard style={{ marginBottom: 28 }}>
          <h2 className="section-title">AI 诊断建议</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12 }}>
            {getApiKey()
              ? 'AI 诊断已包含在本次分析中（无建议）'
              : '首次分析跳过了 AI 诊断。配置 API Key 后点击获取：'}
          </p>
          <button className="btn" onClick={handleFetchDiagnosis}>
            获取 AI 诊断
          </button>
          {aiLoading && <div className="spinner" style={{ marginTop: 12 }} />}
        </GlassCard>
      )}
      {diagnosis.length > 0 && (
        <GlassCard style={{ marginBottom: 28 }}>
          <h2 className="section-title text-gradient-purple">AI 诊断建议</h2>
          {diagnosis.map((s: {
            advice: string; severity: string; estimated_hours: number;
            confidence: number; need_human_review: boolean;
          }, i: number) => (
            <div
              key={i}
              className="diagnosis-card glass-card"
              style={{
                marginBottom: 12,
                padding: '16px 16px 16px 20px',
              }}
            >
              <p style={{ marginBottom: 8 }}>{s.advice}</p>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', fontSize: 12 }}>
                <span className="tag" style={{ background: SEVERITY_COLORS[s.severity] }}>{s.severity}</span>
                <span style={{ color: 'var(--text-secondary)' }}>~{s.estimated_hours}h</span>
                <span style={{ color: s.confidence >= 70 ? 'var(--accent-secondary)' : 'var(--yellow)' }}>
                  置信度 {s.confidence}%
                </span>
                {s.need_human_review && (
                  <span className="tag" style={{ background: 'var(--yellow)', color: '#111' }}>需人工确认</span>
                )}
              </div>
            </div>
          ))}
        </GlassCard>
      )}

      {/* Issues */}
      {allIssues.length > 0 && (
        <GlassCard style={{ marginBottom: 28 }}>
          <h2 className="section-title">问题列表 ({allIssues.length})</h2>
          {allIssues.slice(0, 20).map((issue: string, i: number) => (
            <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: 13, color: 'var(--text-secondary)' }}>
              {issue}
            </div>
          ))}
        </GlassCard>
      )}

      {/* Badge Embed */}
      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title">嵌入 Badge</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12 }}>
          将以下 Markdown 代码添加到你的 README.md 中，实时展示健康状态：
        </p>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12 }}>
          <img
            src={badgeImgUrl}
            alt="health badge"
            style={{ height: 20, borderRadius: 3 }}
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
          />
          <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>← 预览</span>
        </div>
        {/* macOS-style code block header */}
        <div style={{ background: 'var(--bg-surface)', borderRadius: '12px 12px 0 0', border: '1px solid var(--border)', borderBottom: 'none' }}>
          <div className="code-block-header">
            <span className="code-dot code-dot-red" />
            <span className="code-dot code-dot-yellow" />
            <span className="code-dot code-dot-green" />
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'stretch', background: 'var(--bg-surface)', borderRadius: '0 0 12px 12px', border: '1px solid var(--border)', borderTop: 'none', padding: 12 }}>
          <code className="code-block" style={{ border: 'none', borderRadius: 0, background: 'transparent', padding: 0 }}>{badgeMd}</code>
          <button className="btn btn-sm" onClick={copyBadge} style={{ alignSelf: 'center' }}>
            {copied ? '已复制' : '复制'}
          </button>
        </div>
      </GlassCard>

      {/* Share Result */}
      <GlassCard>
        <h2 className="section-title">分享结果</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12 }}>
          复制此链接分享给他人，打开后自动触发分析
        </p>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <code className="code-block">{window.location.href}</code>
          <button
            className="btn btn-sm"
            onClick={() => {
              navigator.clipboard.writeText(window.location.href).then(() => {
                setShareCopied(true);
                setTimeout(() => setShareCopied(false), 2000);
              });
            }}
          >
            {shareCopied ? '链接已复制' : '复制链接'}
          </button>
        </div>
      </GlassCard>
    </div>
  );
}
