export default function AboutPage() {
  return (
    <div className="page-container fade-in">
      <h1>关于 Repo Health Check</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32, lineHeight: 1.7 }}>
        一个开源仓库健康体检工具，通过 6 个维度自动分析 GitHub 仓库的代码质量、测试覆盖、
        架构健康、文档完整性、依赖安全和工程规范，生成雷达图、健康徽章和 AI 诊断建议。
      </p>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2 className="section-title">🏗️ 技术栈</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
          {[
            { label: '后端', items: 'Python 3.11+ / FastAPI / uvicorn' },
            { label: '分析引擎', items: 'radon / lizard / bandit / pip-audit' },
            { label: '前端', items: 'React 18 / TypeScript / Vite / ECharts' },
            { label: 'AI', items: 'OpenAI / DeepSeek API' },
            { label: '存储', items: 'JSON 文件 / 内存缓存' },
            { label: '部署', items: 'Docker Compose / Vercel' },
          ].map((t) => (
            <div key={t.label} style={{ padding: 12 }}>
              <span style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>{t.label}</span>
              <span style={{ fontSize: 13, fontWeight: 600 }}>{t.items}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2 className="section-title">📐 SDD 开发流程</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
          本项目使用 OpenSpec 规范驱动开发（SDD），共 10 个 capability 迭代交付。
        </p>
        <div style={{ display: 'grid', gap: 4 }}>
          {[
            'cap-01-project-init · 前后端骨架',
            'cap-02-analysis-engine · 6 维分析器',
            'cap-03-api-report · API + Badge',
            'cap-04-ai-diagnosis · LLM 诊断',
            'cap-05-frontend-polish · 暗色 UI',
            'cap-06-deploy-e2e · 部署 + e2e',
            'cap-07-polish-final · 持久化/社区',
            'cap-08-async-optimize · async 重构',
            'cap-09-backend-frontend-optimize · 优化',
            'cap-10-theme-oauth-deploy · 主题/OAuth',
          ].map((cap, i) => (
            <div
              key={cap}
              style={{
                padding: '8px 14px',
                borderRadius: 6,
                background: 'var(--bg)',
                fontSize: 13,
                display: 'flex',
                alignItems: 'center',
                gap: 10,
              }}
            >
              <span className="badge" style={{ background: 'var(--accent)', fontSize: 11, padding: '1px 8px', minWidth: 24, textAlign: 'center' }}>
                {i + 1}
              </span>
              <span style={{ color: 'var(--text)' }}>{cap.split(' · ')[0]}</span>
              <span style={{ color: 'var(--text-secondary)', marginLeft: 'auto', fontSize: 12 }}>{cap.split(' · ')[1]}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2 className="section-title">🤝 贡献</h2>
        <div style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.7 }}>
          <p>欢迎通过以下方式参与：</p>
          <ul style={{ paddingLeft: 20, marginTop: 8 }}>
            <li>提交 Bug 或 Feature Request → <a href="https://github.com/user/repo-health-check/issues" target="_blank" style={{ color: 'var(--accent)' }}>GitHub Issues</a></li>
            <li>Fork 仓库 → 创建 feature 分支 → 提交 PR</li>
            <li>分析你的仓库，在 Issue 中贴出 Badge</li>
            <li>参与 <a href="https://github.com/user/repo-health-check/blob/main/community/challenge.md" target="_blank" style={{ color: 'var(--accent)' }}>2 周挑战赛</a></li>
          </ul>
        </div>
      </div>
    </div>
  );
}
