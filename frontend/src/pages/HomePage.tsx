import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getApiKey, setApiKey, clearApiKey } from '../api';

const GITHUB_URL_RE = /^https?:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;

// GitHub 高分项目推荐（精选体积适中、分析速度快的项目）
const RECOMMENDED_REPOS = [
  { owner: 'vuejs', repo: 'vue', stars: '212K', lang: 'TypeScript', color: '#3178c6', desc: '渐进式前端框架' },
  { owner: 'facebook', repo: 'react', stars: '236K', lang: 'JavaScript', color: '#f7df1e', desc: '声明式UI库' },
  { owner: 'expressjs', repo: 'express', stars: '67K', lang: 'JavaScript', color: '#f7df1e', desc: 'Node.js Web框架' },
  { owner: 'redis', repo: 'redis', stars: '69K', lang: 'C', color: '#555555', desc: '高性能KV数据库' },
  { owner: 'fastify', repo: 'fastify', stars: '33K', lang: 'JavaScript', color: '#f7df1e', desc: '高速Node.js框架' },
  { owner: 'pallets', repo: 'flask', stars: '70K', lang: 'Python', color: '#3572A5', desc: '轻量Python Web框架' },
  { owner: 'psf', repo: 'requests', stars: '53K', lang: 'Python', color: '#3572A5', desc: 'Python HTTP库' },
  { owner: 'prettier', repo: 'prettier', stars: '51K', lang: 'JavaScript', color: '#f7df1e', desc: '代码格式化工具' },
  { owner: 'axios', repo: 'axios', stars: '107K', lang: 'JavaScript', color: '#f7df1e', desc: 'Promise HTTP客户端' },
  { owner: 'nestjs', repo: 'nest', stars: '71K', lang: 'TypeScript', color: '#3178c6', desc: '企业级Node.js框架' },
  { owner: 'remix-run', repo: 'react-router', stars: '54K', lang: 'TypeScript', color: '#3178c6', desc: 'React路由库' },
  { owner: 'tiangolo', repo: 'fastapi', stars: '84K', lang: 'Python', color: '#3572A5', desc: '高性能Python API' },
];

export default function HomePage() {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [savedKey, setSavedKey] = useState(getApiKey());
  const [keyInput, setKeyInput] = useState(savedKey);
  const [showKeyConfig, setShowKeyConfig] = useState(false);
  const [keySaved, setKeySaved] = useState(false);
  const navigate = useNavigate();

  const isValid = GITHUB_URL_RE.test(url.trim());
  const showError = !isValid && url.trim().length > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('请输入 GitHub 仓库 URL');
      return;
    }
    if (!isValid) {
      setError('请输入有效的 GitHub URL（如 https://github.com/user/repo）');
      return;
    }
    setError('');
    const repoId = encodeURIComponent(url.trim());
    navigate(`/report/${repoId}`);
  };

  const handleSaveKey = () => {
    if (keyInput.trim()) {
      setApiKey(keyInput.trim());
      setSavedKey(keyInput.trim());
      setKeySaved(true);
      setTimeout(() => setKeySaved(false), 2000);
    } else {
      clearApiKey();
      setSavedKey('');
    }
  };

  const hasKey = savedKey.length > 0;

  return (
    <div className="page-container home-page fade-in">
      <div className="hero">
        <h1 className="hero-title">Repo Health Check</h1>
        <p className="hero-subtitle">
          输入 GitHub 仓库 URL，6 个维度全面体检，AI 智能诊断，生成健康 Badge
        </p>
      </div>

      <div className="card" style={{ maxWidth: 560, margin: '0 auto' }}>
        <form onSubmit={handleSubmit}>
          <div style={{ position: 'relative', marginBottom: 16 }}>
            <input
              type="text"
              placeholder="https://github.com/user/repo"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                setError('');
              }}
              className={`input ${showError || error ? 'input-error' : ''}`}
              autoFocus
            />
          </div>

          {error && (
            <div className="error-toast" style={{ marginBottom: 16 }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', display: 'flex', alignItems: 'center', gap: 8 }}
          >
            🔍 开始体检
          </button>
        </form>

        {/* API Key Configuration */}
        <div style={{ marginTop: 20, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
          <div
            onClick={() => setShowKeyConfig(!showKeyConfig)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              fontSize: 13,
              color: 'var(--text-secondary)',
              userSelect: 'none',
            }}
          >
            <span>
              🤖 AI 诊断配置
              {hasKey && (
                <span style={{ color: 'var(--green)', marginLeft: 8, fontSize: 12 }}>已配置</span>
              )}
            </span>
            <span style={{ transform: showKeyConfig ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }}>
              ▶
            </span>
          </div>
          {showKeyConfig && (
            <div style={{ marginTop: 12 }}>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
                配置 DeepSeek API Key 以启用 AI 智能诊断功能。Key 仅保存在本地浏览器中。
              </p>
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  type="password"
                  placeholder="sk-your-deepseek-key"
                  value={keyInput}
                  onChange={(e) => setKeyInput(e.target.value)}
                  className="input"
                  style={{ flex: 1, fontSize: 13, padding: '10px 12px' }}
                />
                <button
                  type="button"
                  className="btn btn-sm"
                  onClick={handleSaveKey}
                  style={{ whiteSpace: 'nowrap' }}
                >
                  {keySaved ? '✓ 已保存' : '保存'}
                </button>
              </div>
              {hasKey && (
                <p style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 6 }}>
                  已配置 Key ({savedKey.slice(0, 8)}...)。AI 诊断将在分析完成后自动触发。
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Recommended repos - GitHub 高分项目 */}
      <div style={{ maxWidth: 560, margin: '24px auto 0' }}>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 10, textAlign: 'center' }}>
          GitHub 高分项目推荐
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 10 }}>
          {RECOMMENDED_REPOS.map((item) => {
            const fullUrl = `https://github.com/${item.owner}/${item.repo}`;
            return (
              <button
                key={fullUrl}
                className="card card-hover"
                onClick={() => {
                  setUrl(fullUrl);
                }}
                style={{
                  padding: '12px 14px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-card)',
                  color: 'var(--text)',
                  cursor: 'pointer',
                  borderRadius: 10,
                  fontSize: 13,
                  fontFamily: 'inherit',
                  textAlign: 'left',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 8,
                }}
              >
                <div style={{ overflow: 'hidden', flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.owner}/{item.repo}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
                    ⭐ {item.stars}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.desc}
                  </div>
                </div>
                <span
                  style={{
                    background: item.color,
                    color: '#fff',
                    fontSize: 10,
                    fontWeight: 600,
                    padding: '2px 6px',
                    borderRadius: 4,
                    flexShrink: 0,
                  }}
                >
                  {item.lang}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Feature highlights */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16, maxWidth: 560, margin: '32px auto 0' }}>
        {[
          { icon: '📊', label: '六维雷达图' },
          { icon: '🤖', label: 'AI 诊断' },
          { icon: '🏆', label: '排行榜' },
          { icon: '🏷️', label: '徽章生成' },
        ].map((f) => (
          <div key={f.label} className="card card-hover" style={{ textAlign: 'center', padding: 20 }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>{f.icon}</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{f.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
