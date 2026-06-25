import GlassCard from '../components/GlassCard';

const TECH_STACK = [
  { label: '后端', items: 'Python 3.11+ / FastAPI / uvicorn / SQLite', align: 'left' },
  { label: '分析引擎', items: 'radon / lizard / bandit / pip-audit / 多语言统计', align: 'right' },
  { label: '前端', items: 'React 18 / TypeScript / Vite / ECharts / Canvas', align: 'left' },
  { label: 'AI 诊断', items: 'DeepSeek / OpenAI / 无 Key 本地规则诊断', align: 'right' },
  { label: '安全', items: 'XSS 转义 / Session 强密钥 / OAuth state / CORS 白名单', align: 'left' },
  { label: '工程化', items: 'OpenSpec / GitHub Actions / GitLink DevOps / pytest / Vitest', align: 'right' },
  { label: '分享能力', items: 'HTML 报告 / PDF 打印 / Wrapped 分享卡片 / PK 海报', align: 'left' },
  { label: '本地体验', items: '一键启动 / 缓存感知分析 / 分步进度 / 榜单分页', align: 'right' },
];

const HIGHLIGHTS = [
  '输入 GitHub 仓库 URL，即可生成 6 维健康度报告、雷达图、语言分布和问题列表。',
  '报告页支持 30 分钟缓存感知加载，刷新页面不会反复克隆和分析同一仓库。',
  'AI 诊断自动执行：无 API Key 时使用本地规则，有 DeepSeek Key 时升级为 LLM 建议。',
  '支持 HTML/PDF 导出、README Badge、分享卡片和仓库 PK 海报。',
  '排行榜支持投票、分页和趋势展示，Compare 页面支持快捷预填与并行分析。',
  '安全层完成 XSS 防护、Session 密钥强校验、pending task 锁保护与缓存深拷贝。',
  '工程侧补齐 GitHub Actions、GitLink DevOps 使用说明、CONTRIBUTING / SECURITY / CHANGELOG。',
];

const CAPABILITIES = [
  { id: 'cap-01', name: 'project-init', desc: '前后端骨架、基础 API、OpenSpec 项目结构与启动流程。' },
  { id: 'cap-02', name: 'analysis-engine', desc: '代码质量、测试覆盖、架构、文档、依赖安全、工程规范 6 维分析。' },
  { id: 'cap-03', name: 'api-report', desc: '分析聚合 API、缓存、Badge SVG、HTML 报告和历史记录。' },
  { id: 'cap-04', name: 'ai-diagnosis', desc: 'AI 诊断接口、建议结构化输出、置信度与人工复核标记。' },
  { id: 'cap-05', name: 'frontend-polish', desc: '暗色玻璃拟态 UI、雷达图、排行榜、报告页与真实 API 串联。' },
  { id: 'cap-06', name: 'deploy-e2e', desc: 'Docker / 部署脚本 / E2E 自测流程，支持本地和线上验证。' },
  { id: 'cap-07', name: 'polish-final', desc: 'Compare、历史趋势、投票系统和 JavaScript/TypeScript 深度分析。' },
  { id: 'cap-08', name: 'async-optimize', desc: '异步分析任务、状态轮询和分析流程性能优化。' },
  { id: 'cap-09', name: 'backend-frontend-optimize', desc: '前后端交互、错误态、加载态和体验细节优化。' },
  { id: 'cap-10', name: 'theme-oauth-deploy', desc: '主题切换、GitHub OAuth、部署配置和认证体验完善。' },
  { id: 'cap-11', name: 'discover-about', desc: '发现入口、关于页、项目说明和贡献引导。' },
  { id: 'cap-12', name: 'bugfix-quality', desc: '集中修复已知 Bug，提升分析稳定性和页面质量。' },
  { id: 'cap-13', name: 'quality-polish', desc: '细节打磨、边界状态、页面文案和视觉一致性。' },
  { id: 'cap-14', name: 'proxy-auto-degrade', desc: 'Git 代理自动降级、缓存修复和克隆失败兜底。' },
  { id: 'cap-15', name: 'curved-loop-hero', desc: 'CurvedLoop 首页标题与视觉表现增强。' },
  { id: 'cap-16', name: 'react-bits-visual-redesign', desc: 'Iridescence WebGL 背景、Dock 导航、GlassCard、AnimatedCounter。' },
  { id: 'cap-17', name: 'readme-screenshots', desc: '双语 README、页面截图和项目展示材料。' },
  { id: 'cap-18', name: 'xss-security-fix', desc: 'Badge SVG 与 HTML 导出内容转义，修复 XSS 风险。' },
  { id: 'cap-19', name: 'security-architecture-hardening', desc: 'Session 强密钥、pending task 锁、缓存深拷贝、CI/CD 与文档补全。' },
  { id: 'cap-20', name: 'report-leaderboard-ux', desc: '缓存感知报告、自动 AI、进度条、PDF/分享卡片、语言饼图、榜单分页。' },
];

export default function AboutPage() {
  return (
    <div className="page-container fade-in stagger-children">
      <h1 className="text-gradient">关于 Repo Health Check</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32, lineHeight: 1.8 }}>
        Repo Health Check 是一个面向开源项目的仓库健康度体检工具。它会从代码质量、测试覆盖、
        架构健康、文档完整、依赖安全和工程规范六个维度分析 GitHub 仓库，并把结果转成可视化报告、
        AI 改进建议、README Badge、排行榜、对比 PK 和可分享资产。
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
        <div className="about-tech-grid">
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
          当前已归档 {CAPABILITIES.length} 个 capability。
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
