import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { API_BASE, getApiKey, sha256Prefix } from '../api';
import { useApp, type AIDiagnosisItem, type AnalysisDimension } from '../context/AppContext';
import AnimatedCounter from '../components/AnimatedCounter';
import GlassCard from '../components/GlassCard';
import HistoryChart from '../components/HistoryChart';
import LanguagePieChart from '../components/LanguagePieChart';
import RadarChart from '../components/RadarChart';
import ScoreBar from '../components/ScoreBar';
import {
  downloadShareCard,
  extractLanguageBreakdown,
  normalizeBadgeColor,
  openPdfPrintDialog,
} from '../utils/reportAssets';

const SEVERITY_COLORS: Record<string, string> = {
  high: 'var(--red)',
  medium: 'var(--yellow)',
  low: 'var(--blue)',
};

const PROGRESS_STEPS = [
  { label: '连接缓存', hint: '正在检查 30 分钟内是否已有分析结果' },
  { label: '克隆仓库', hint: '正在拉取仓库内容' },
  { label: '分析代码', hint: '正在计算质量、测试、文档、安全等维度' },
  { label: 'AI 诊断', hint: '正在生成改进建议，可用后会自动合并到报告' },
  { label: '生成报告', hint: '正在整理可视化报告' },
];

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

export default function ReportPage() {
  const { repoId } = useParams<{ repoId: string }>();
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const repoUrl = repoId ? decodeURIComponent(repoId) : '';

  const [copied, setCopied] = useState(false);
  const [shareCopied, setShareCopied] = useState(false);
  const [assetError, setAssetError] = useState('');
  const [history, setHistory] = useState<
    Array<{ analyzed_at: string; health_score: number; badge_level: string }>
  >([]);
  const [badgeHash, setBadgeHash] = useState('');
  const [progressIndex, setProgressIndex] = useState(0);

  useEffect(() => {
    if (!repoUrl) return;

    let cancelled = false;
    dispatch({ type: 'RESET' });
    dispatch({ type: 'START_ANALYSIS' });
    setProgressIndex(0);

    const run = async () => {
      const apiKey = getApiKey();

      try {
        const resp = await fetch(`${API_BASE}/api/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            repo_url: repoUrl,
            force_sync: false,
            skip_ai: false,
            ai_api_key: apiKey || undefined,
          }),
        });
        const json = await resp.json();

        if (cancelled) return;

        if (json.code === 0 && json.data) {
          setProgressIndex(4);
          dispatch({ type: 'ANALYSIS_SUCCESS', payload: json.data });
          return;
        }

        if (json.code !== 1 || !json.data?.task_id) {
          dispatch({ type: 'ANALYSIS_ERROR', payload: json.message || '请求失败' });
          return;
        }

        const taskId = json.data.task_id as string;
        const started = Date.now();
        let attempts = 0;

        while (!cancelled && Date.now() - started < 180000) {
          await sleep(2000);
          attempts += 1;
          if (attempts >= 2) setProgressIndex(1);
          if (attempts >= 5) setProgressIndex(2);
          if (attempts >= 10) setProgressIndex(3);

          const statusResp = await fetch(
            `${API_BASE}/api/analyze/status?task_id=${encodeURIComponent(taskId)}&repo_url=${encodeURIComponent(repoUrl)}`,
          );
          const statusJson = await statusResp.json();
          const status = statusJson.data?.status;

          if (status === 'completed' && statusJson.data?.result) {
            setProgressIndex(4);
            dispatch({ type: 'ANALYSIS_SUCCESS', payload: statusJson.data.result });
            return;
          }

          if (status === 'failed') {
            dispatch({
              type: 'ANALYSIS_ERROR',
              payload: statusJson.data?.error || '分析失败',
            });
            return;
          }
        }

        if (!cancelled) {
          dispatch({ type: 'ANALYSIS_ERROR', payload: '分析超时，请稍后重试' });
        }
      } catch {
        if (!cancelled) {
          dispatch({ type: 'ANALYSIS_ERROR', payload: '无法连接后端服务' });
        }
      }
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [dispatch, repoUrl]);

  useEffect(() => {
    if (!repoUrl || state.status !== 'success') return;
    fetch(`${API_BASE}/api/history/${encodeURIComponent(repoUrl)}`)
      .then((r) => r.json())
      .then((json) => setHistory(json.data || []))
      .catch(() => {});
  }, [repoUrl, state.status]);

  useEffect(() => {
    if (repoUrl) {
      sha256Prefix(repoUrl).then(setBadgeHash);
    }
  }, [repoUrl]);

  const badgeMd = `![health](${API_BASE}/api/badge/${badgeHash})`;
  const badgeImgUrl = `${API_BASE}/api/badge/${badgeHash}`;
  const currentStep = PROGRESS_STEPS[progressIndex];

  const data = state.analysisResult;
  const dimensions = useMemo(() => data?.dimensions || [], [data?.dimensions]);
  const radarData = useMemo(
    () => dimensions.map((d: AnalysisDimension) => ({ name: d.dimension, score: d.score })),
    [dimensions],
  );
  const diagnosis = data?.ai_diagnosis || [];
  const languageData = useMemo(() => extractLanguageBreakdown(dimensions), [dimensions]);
  const allIssues = useMemo(
    () =>
      dimensions.flatMap((d: AnalysisDimension) =>
        (d.issues || []).map((issue: string) => `[${d.dimension}] ${issue}`),
      ),
    [dimensions],
  );

  const copyBadge = () => {
    navigator.clipboard.writeText(badgeMd).then(() => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    });
  };

  const exportReport = () => {
    const link = document.createElement('a');
    link.href = `${API_BASE}/api/export/${badgeHash}`;
    link.download = `repo-health-report-${repoUrl.replace('https://github.com/', '').replace('/', '-')}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportPdfReport = async () => {
    setAssetError('');
    try {
      await openPdfPrintDialog(`${API_BASE}/api/export/${badgeHash}`);
    } catch {
      setAssetError('PDF 导出窗口被拦截或报告加载失败，请允许弹窗后重试。');
    }
  };

  const handleDownloadShareCard = () => {
    if (!data) return;
    setAssetError('');
    downloadShareCard(data, languageData);
  };

  if (state.status === 'loading') {
    return (
      <div className="page-container" style={{ paddingTop: 80 }}>
        <GlassCard style={{ maxWidth: 620, margin: '0 auto' }}>
          <div className="analysis-progress-head">
            <div className="spinner" />
            <div>
              <h1 style={{ marginBottom: 6 }}>正在生成体检报告</h1>
              <p style={{ color: 'var(--text-secondary)', wordBreak: 'break-all' }}>{repoUrl}</p>
            </div>
          </div>
          <div className="analysis-progress-bar" aria-label="分析进度">
            <div style={{ width: `${((progressIndex + 1) / PROGRESS_STEPS.length) * 100}%` }} />
          </div>
          <div className="analysis-steps">
            {PROGRESS_STEPS.map((step, index) => (
              <div
                key={step.label}
                className={`analysis-step ${index < progressIndex ? 'done' : ''} ${index === progressIndex ? 'active' : ''}`}
              >
                <span>{index < progressIndex ? '✓' : index + 1}</span>
                <div>
                  <strong>{step.label}</strong>
                  <p>{index === progressIndex ? currentStep.hint : step.hint}</p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    );
  }

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

  if (!data) return null;

  return (
    <div className="page-container fade-in stagger-children">
      <button className="btn-back" onClick={() => navigate('/')}>← 返回</button>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 20, flexWrap: 'wrap', marginBottom: 8 }}>
        <h1 className="text-gradient-purple">体检报告</h1>
        <span className="badge-glow" style={{ background: data.badge_color === 'lightgrey' ? '#9f9f9f' : data.badge_color }}>
          {data.badge_level}
        </span>
        <span className="score-number text-gradient">
          <AnimatedCounter target={data.health_score} decimals={0} />
        </span>
        <span className="score-label">/100</span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button className="btn btn-sm" onClick={() => navigate(`/compare?repo_a=${encodeURIComponent(repoUrl)}`)}>
            与另一个仓库对比
          </button>
          <button onClick={exportReport} className="btn btn-sm">
            导出报告
          </button>
          <button onClick={exportPdfReport} className="btn btn-sm">
            导出 PDF
          </button>
          <button onClick={handleDownloadShareCard} className="btn btn-sm">
            生成分享卡片
          </button>
        </div>
      </div>
      <p className="repo-url">{repoUrl}</p>
      {assetError && <div className="error-toast" style={{ marginBottom: 16 }}>{assetError}</div>}

      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">六维度雷达图</h2>
        <RadarChart dimensions={radarData} />
      </GlassCard>

      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title">语言分布</h2>
        <LanguagePieChart data={languageData} />
      </GlassCard>

      {dimensions.length > 0 && (
        <GlassCard style={{ marginBottom: 28 }}>
          <h2 className="section-title">各维度详情</h2>
          {dimensions.map((d: AnalysisDimension) => (
            <ScoreBar key={d.dimension} label={d.dimension} score={d.score} />
          ))}
        </GlassCard>
      )}

      {history.length >= 1 && <HistoryChart history={history} />}

      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">AI 诊断建议</h2>
        {diagnosis.length > 0 ? (
          diagnosis.map((s: AIDiagnosisItem, i: number) => (
            <div key={i} className="diagnosis-card glass-card" style={{ marginBottom: 12, padding: '16px 16px 16px 20px' }}>
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
          ))
        ) : (
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
            本次分析未返回诊断建议。无 Key 时系统会自动使用本地规则诊断；配置 DeepSeek Key 后会升级为 LLM 诊断。
          </p>
        )}
      </GlassCard>

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

      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title">嵌入 Badge</h2>
        <div className="badge-preview-card" style={{ borderColor: data.badge_color }}>
          <div>
            <span className="badge-preview-dot" style={{ background: normalizeBadgeColor(data.badge_color) }} />
            <strong>{data.badge_level}</strong>
            <span>{Math.round(data.health_score)}/100</span>
          </div>
          <img
            src={badgeImgUrl}
            alt="health badge"
            style={{ height: 20, borderRadius: 3 }}
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
          />
        </div>
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

      <GlassCard>
        <h2 className="section-title">分享结果</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <code className="code-block">{window.location.href}</code>
          <button
            className="btn btn-sm"
            onClick={() => {
              navigator.clipboard.writeText(window.location.href).then(() => {
                setShareCopied(true);
                window.setTimeout(() => setShareCopied(false), 2000);
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
