import GlassCard from '../components/GlassCard';

const TECH_STACK = [
  { label: '后端', items: 'Python 3.11+ / FastAPI / uvicorn', align: 'left' },
  { label: '分析引擎', items: 'radon / lizard / bandit / pip-audit', align: 'right' },
  { label: '前端', items: 'React 18 / TypeScript / Vite / ECharts', align: 'left' },
  { label: 'AI 诊断', items: 'OpenAI / DeepSeek API', align: 'right' },
  { label: '认证', items: 'GitHub OAuth + itsdangerous session', align: 'left' },
  { label: '工程管理', items: 'OpenSpec（capability 归档 + specs 规范）', align: 'right' },
  { label: '存储', items: 'JSON 文件 + 内存缓存（TTL 30min）', align: 'left' },
  { label: '部署', items: 'Docker Compose / Vercel', align: 'right' },
];

const CAPABILITIES = [
  { id: 'cap-01', name: 'project-init', desc: '前后端骨架搭建' },
  { id: 'cap-02', name: 'analysis-engine', desc: '6 维分析器引擎' },
  { id: 'cap-03', name: 'api-report', desc: 'API + Badge + 报告' },
  { id: 'cap-04', name: 'ai-diagnosis', desc: 'LLM 智能诊断' },
  { id: 'cap-05', name: 'frontend-polish', desc: '暗色主题 UI' },
  { id: 'cap-06', name: 'deploy-e2e', desc: '部署 + E2E 测试' },
  { id: 'cap-07', name: 'polish-final', desc: '持久化/社区功能' },
  { id: 'cap-08', name: 'async-optimize', desc: 'async 重构优化' },
  { id: 'cap-09', name: 'backend-frontend-optimize', desc: '前后端细节优化' },
  { id: 'cap-10', name: 'theme-oauth-deploy', desc: '主题/OAuth/部署' },
  { id: 'cap-11', name: 'discover-about', desc: '发现页/关于页' },
  { id: 'cap-12', name: 'bugfix-quality', desc: 'Bug 修复与质量提升' },
  { id: 'cap-13', name: 'quality-polish', desc: '细节打磨' },
  { id: 'cap-14', name: 'proxy-auto-degrade', desc: '代理自动降级 + 缓存修复' },
  { id: 'cap-15', name: 'normalize-cache', desc: '缓存规范化 + 分析守卫' },
];

export default function AboutPage() {
  return (
    <div className="page-container fade-in stagger-children">
      <h1 className="text-gradient">关于 Repo Health Check</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32, lineHeight: 1.7 }}>
        一个开源仓库健康体检工具，通过 6 个维度自动分析 GitHub 仓库的代码质量、测试覆盖、
        架构健康、文档完整性、依赖安全和工程规范，生成雷达图、健康徽章和 AI 诊断建议。
      </p>

      {/* Tech Stack — staggered left/right layout */}
      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">技术栈</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          {TECH_STACK.map((t) => (
            <div
              key={t.label}
              className="feature-card"
              style={{
                padding: 16,
                textAlign: t.align === 'right' ? 'right' : 'left',
              }}
            >
              <span style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>{t.label}</span>
              <span style={{ fontSize: 13, fontWeight: 600 }}>{t.items}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* SDD Timeline */}
      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">SDD 开发流程</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 20 }}>
          本项目使用 OpenSpec 规范驱动开发（SDD），共 {CAPABILITIES.length} 个 capability 迭代交付。
        </p>
        <div className="timeline">
          {CAPABILITIES.map((cap) => (
            <div key={cap.id} className="timeline-item">
              <div className="timeline-item-title">
                <span style={{ color: 'var(--accent)', fontSize: 12, fontWeight: 700 }}>{cap.id}</span>
                <span style={{ marginLeft: 8 }}>{cap.name}</span>
              </div>
              <div className="timeline-item-desc">{cap.desc}</div>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Contributions */}
      <GlassCard>
        <h2 className="section-title">贡献</h2>
        <div style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.8 }}>
          <p>欢迎通过以下方式参与：</p>
          <ul style={{ paddingLeft: 20, marginTop: 8 }}>
            <li>提交 Bug 或 Feature Request → <a href="https://github.com/LING-lab72/repo-health-check/issues" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>GitHub Issues</a></li>
            <li>Fork 仓库 → 创建 feature 分支 → 提交 PR</li>
            <li>分析你的仓库，在 Issue 中贴出 Badge</li>
            <li>参与 <a href="https://github.com/LING-lab72/repo-health-check/blob/main/community/challenge.md" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>2 周挑战赛</a></li>
          </ul>
        </div>
      </GlassCard>
    </div>
  );
}
