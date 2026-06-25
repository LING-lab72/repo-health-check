import '@testing-library/jest-dom/vitest';
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import GlassCard from '../components/GlassCard';
import LanguagePieChart from '../components/LanguagePieChart';
import RadarChart from '../components/RadarChart';
import ScoreBar from '../components/ScoreBar';
import { estimatePeerPercentile, extractLanguageBreakdown, normalizeBadgeColor } from '../utils/reportAssets';

describe('core components', () => {
  it('renders ScoreBar as an accessible progressbar', () => {
    render(<ScoreBar label="code_quality" score={82} />);

    const bar = screen.getByRole('progressbar', { name: '代码质量得分' });
    expect(bar).toHaveAttribute('aria-valuenow', '82');
  });

  it('supports keyboard activation for clickable GlassCard', () => {
    const onClick = vi.fn();
    render(<GlassCard onClick={onClick}>Open</GlassCard>);

    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: 'Enter' });
    fireEvent.keyDown(card, { key: ' ' });

    expect(onClick).toHaveBeenCalledTimes(2);
  });

  it('renders an empty state for RadarChart without dimensions', () => {
    render(<RadarChart dimensions={[]} />);

    expect(screen.getByText('暂无数据')).toBeInTheDocument();
  });

  it('renders an empty state for LanguagePieChart without data', () => {
    render(<LanguagePieChart data={[]} />);

    expect(screen.getByText('暂无语言分布数据')).toBeInTheDocument();
  });

  it('extracts language breakdown from code quality details', () => {
    const result = extractLanguageBreakdown([
      {
        dimension: 'code_quality',
        score: 80,
        issues: [],
        details: {
          language_breakdown: { python: 3, js_ts: 2, other: 0 },
        },
      },
    ]);

    expect(result).toEqual([
      { label: 'Python', value: 3 },
      { label: 'JavaScript/TypeScript', value: 2 },
    ]);
  });

  it('normalizes badge color names for canvas and previews', () => {
    expect(normalizeBadgeColor('brightgreen')).toBe('#22c55e');
    expect(normalizeBadgeColor('#123456')).toBe('#123456');
  });

  it('estimates wrapped-style peer percentile from score', () => {
    expect(estimatePeerPercentile(85)).toBe(90);
    expect(estimatePeerPercentile(100)).toBe(99);
    expect(estimatePeerPercentile(-10)).toBe(1);
  });
});
