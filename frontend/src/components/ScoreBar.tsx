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
  if (score >= 75) return 'var(--green)';
  if (score >= 50) return 'var(--yellow)';
  return 'var(--red)';
}

export default function ScoreBar({ label, score }: Props) {
  const displayLabel = DIM_LABELS[label] || label;
  const color = getColor(score);

  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>{displayLabel}</span>
        <span style={{ fontWeight: 700, color }}>{score}/100</span>
      </div>
      <div
        style={{
          height: 8,
          borderRadius: 4,
          background: 'rgba(148,163,184,0.15)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${score}%`,
            borderRadius: 4,
            background: color,
            transition: 'width 1s ease',
          }}
        />
      </div>
    </div>
  );
}
