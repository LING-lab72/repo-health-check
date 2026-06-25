interface Props {
  label: string;
  score: number;
}

const DIM_LABELS: Record<string, string> = {
  code_quality: '代码质量',
  test_coverage: '测试覆盖',
  architecture: '架构健康',
  documentation: '文档完整',
  dependency_security: '依赖安全',
  engineering: '工程规范',
};

function getColor(score: number) {
  if (score >= 75) return 'var(--accent-secondary)';
  if (score >= 50) return 'var(--yellow)';
  return 'var(--red)';
}

function getGradient(score: number) {
  if (score >= 75) return 'linear-gradient(90deg, var(--accent-secondary), #06b6d4)';
  if (score >= 50) return 'linear-gradient(90deg, var(--yellow), #fbbf24)';
  return 'linear-gradient(90deg, var(--red), #f97316)';
}

export default function ScoreBar({ label, score }: Props) {
  const displayLabel = DIM_LABELS[label] || label;
  const color = getColor(score);
  const gradient = getGradient(score);

  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)' }}>{displayLabel}</span>
        <span style={{ fontWeight: 800, color, fontVariantNumeric: 'tabular-nums' }}>{score}/100</span>
      </div>
      <div
        className="score-bar-track"
        role="progressbar"
        aria-label={`${displayLabel}得分`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.max(0, Math.min(100, score))}
      >
        <div
          className="score-bar-fill"
          style={{
            width: `${score}%`,
            background: gradient,
          }}
        />
      </div>
    </div>
  );
}
