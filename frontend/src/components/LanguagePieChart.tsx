import { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { PieChart } from 'echarts/charts';
import { LegendComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { LanguageDatum } from '../utils/reportAssets';

echarts.use([PieChart, TooltipComponent, LegendComponent, CanvasRenderer]);

interface Props {
  data: LanguageDatum[];
}

const COLORS = ['#60a5fa', '#fbbf24', '#34d399', '#f87171', '#a78bfa', '#fb923c'];

export default function LanguagePieChart({ data }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const hasData = data.length > 0;

  useEffect(() => {
    if (!chartRef.current || !hasData) return;
    const chart = echarts.init(chartRef.current);
    chartInstance.current = chart;

    chart.setOption({
      color: COLORS,
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(15,23,42,0.86)',
        borderColor: 'rgba(99,102,241,0.3)',
        textStyle: { color: '#e2e8f0' },
      },
      legend: {
        bottom: 0,
        textStyle: { color: '#94a3b8', fontSize: 12 },
      },
      series: [
        {
          name: '语言分布',
          type: 'pie',
          radius: ['44%', '72%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: true,
          label: {
            formatter: '{b}\n{d}%',
            color: '#cbd5e1',
            fontSize: 12,
          },
          labelLine: { lineStyle: { color: 'rgba(203,213,225,0.35)' } },
          data: data.map((item) => ({ name: item.label, value: item.value })),
        },
      ],
    });

    return () => {
      chart.dispose();
      chartInstance.current = null;
    };
  }, [data, hasData]);

  useEffect(() => {
    const el = chartRef.current;
    if (!el || !hasData) return;
    const observer = new ResizeObserver(() => chartInstance.current?.resize());
    observer.observe(el);
    return () => observer.disconnect();
  }, [hasData]);

  if (!hasData) {
    return (
      <div className="chart-empty" role="status">
        暂无语言分布数据
      </div>
    );
  }

  return (
    <div
      ref={chartRef}
      role="img"
      aria-label="仓库语言分布饼图"
      style={{ width: '100%', height: 320 }}
    />
  );
}
