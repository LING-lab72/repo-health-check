import GlassCard from '../components/GlassCard';

const TECH_STACK = [
  { label: '后端', items: 'Python 3.11+ / FastAPI / uvicorn / SQLite', align: 'left' },
  { label: '分析引擎', items: 'radon / lizard / bandit / pip-audit / ESLint / madge', align: 'right' },
  { label: '前端', items: 'React 18 / TypeScript / Vite / ECharts / Canvas', align: 'left' },
  { label: 'AI 诊断', items: 'DeepSeek / OpenAI，可无 Key 自动降级本地规则诊断', align: 'right' },
  { label: '安全', items: 'HTML/SVG 转义 / Session 强密钥 / OAuth state / CORS 白名单', align: 'left' },
  { label: '工程化', items: 'GitHub Actions / pytest / Vitest / OpenSpec', align: 'right' },
  { label: '分享能力', items: 'HTML/PDF 报告 / Wrapped 分享卡片 / 仓库 PK 海报', align: 'left' },
  { label: '本地体验', items: '一键启动脚本 / 缓存感知分析 / 进度条 / 分页榜单', align: 'right' },
];

const CAPABILITIES = [
  { id: 'cap-01', name: 'project-init', desc: '前后端骨架、基础 API 与体检流程搭建' },
  { id: 'cap-02', name: 'analysis-engine', desc: '六维度分析器、评分规则和雷达图报告' },
  { id: 'cap-03', name: 'ai-diagnosis', desc: 'LLM 诊断与无 Key 本地规则诊断降级' },
  { id: 'cap-04', name: 'frontend-experience', desc: '暗色玻璃拟态 UI、Dock 导航、无障碍与错误边界' },
  { id: 'cap-05', name: 'security-hardening', desc: 'XSS 防护、Session 强密钥、OAuth state、代理头信任控制' },
  { id: 'cap-06', name: 'persistent-storage', desc: '从 JSON 文件迁移到 SQLite，支持多进程一致性' },
  { id: 'cap-07', name: 'async-cache', desc: '异步分析、缓存命中跳过重分析、Compare 并行化' },
  { id: 'cap-08', name: 'report-export', desc: 'HTML/PDF 导出、语言分布、Wrapped 分享卡片' },
  { id: 'cap-09', name: 'pk-arena', desc: '仓库 PK 对战动画、赢家展示和 PNG 海报生成' },
  { id: 'cap-10', name: 'devops-docs', desc: 'CI/CD、贡献指南、安全策略、变更日志和一键启动脚本' },
];

const HIGHLIGHTS = [
  '输入 GitHub 仓库即可生成 6 维健康度报告、AI 建议、Badge 和导出报告。',
  '报告页支持缓存感知加载，30 分钟内刷新不会重复克隆和分析。',
  '排行榜已支持 SQLite 持久化、投票冷却、分页和趋势标记。',
  'Compare 页面提供仓库 PK Arena，分析完成后可生成对战海报。',
  '所有重要变更通过 OpenSpec capability 归档，方便追踪设计和任务闭环。',
];

export default function AboutPage() {
  return (
    <div className="page-container fade-in stagger-children">
      <h1 className="text-gradient">关于 Repo Health Check</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32, lineHeight: 1.8 }}>
        Repo Health Check 是一个面向开源项目的仓库健康度体检工具。它会从代码质量、测试覆盖、
        架构健康、文档完整、依赖安全和工程规范六个维度分析 GitHub 仓库，并把结果转成可视化报告、
        AI 改进建议、README Badge、排行榜、对比 PK 和可分享海报。
      </p>

      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">当前成果</h2>
        <div style={{ display: 'grid', gap: 12 }}>
          {HIGHLIGHTS.map((item) => (
            <div key={item} className="timeline-item" style={{ marginBottom: 0 }}>
              <div className="timeline-item-desc">{item}</div>
            </div>
          ))}
        </div>
      </GlassCard>

      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">技术栈</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
          {TECH_STACK.map((t) => (
            <div
              key={t.label}
              className="feature-card"
              style={{
                padding: 16,
                textAlign: t.align === 'right' ? 'right' : 'left',
              }}
            >
              <span style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>
                {t.label}
              </span>
              <span style={{ fontSize: 13, fontWeight: 600 }}>{t.items}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      <GlassCard style={{ marginBottom: 28 }}>
        <h2 className="section-title text-gradient-purple">OpenSpec 交付轨迹</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 20 }}>
          本项目使用 OpenSpec 做规范化管理，每个 capability 都保留 proposal、design、tasks 和规格快照。
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

      <GlassCard>
        <h2 className="section-title">参与贡献</h2>
        <div style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.8 }}>
          <p>欢迎通过以下方式参与：</p>
          <ul style={{ paddingLeft: 20, marginTop: 8 }}>
            <li>提交 Bug 或 Feature Request 到 GitHub Issues</li>
            <li>Fork 仓库，创建 feature 分支并提交 Pull Request</li>
            <li>使用一键启动脚本本地运行并验证新能力</li>
            <li>将生成的 Badge、PDF 报告或 PK 海报分享到你的项目主页</li>
          </ul>
        </div>
      </GlassCard>
    </div>
  );
}
