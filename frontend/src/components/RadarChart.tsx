import { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { RadarChart as ERadarChart } from 'echarts/charts';
import { LegendComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([ERadarChart, TooltipComponent, LegendComponent, CanvasRenderer]);

interface RadarData {
  name: string;
  score: number;
}

interface Props {
  dimensions: RadarData[];
}

export default function RadarChart({ dimensions }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const hasData = !!dimensions?.length;

  useEffect(() => {
    if (!chartRef.current || !hasData) return;
    const chart = echarts.init(chartRef.current);
    chartInstance.current = chart;

    chart.setOption({
      animationDuration: 900,
      animationEasing: 'cubicOut',
      animationDurationUpdate: 650,
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(15,23,42,0.86)',
        borderColor: 'rgba(129,140,248,0.35)',
        textStyle: { color: '#e2e8f0' },
      },
      radar: {
        center: ['50%', '50%'],
        radius: '70%',
        indicator: dimensions.map((d) => ({
          name: d.name,
          max: 100,
        })),
        axisName: { color: '#94a3b8', fontSize: 12, fontWeight: 500 },
        splitArea: {
          areaStyle: {
            color: [
              'rgba(99,102,241,0.03)',
              'rgba(99,102,241,0.06)',
              'rgba(99,102,241,0.09)',
              'rgba(99,102,241,0.12)',
              'rgba(99,102,241,0.15)',
            ],
          },
        },
        splitLine: { lineStyle: { color: 'rgba(148,163,184,0.15)' } },
        axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: dimensions.map((d) => d.score),
              name: '健康度',
              areaStyle: { color: 'rgba(99,102,241,0.22)' },
              lineStyle: { color: '#818cf8', width: 2 },
              itemStyle: {
                color: '#818cf8',
                shadowColor: 'rgba(129,140,248,0.45)',
                shadowBlur: 10,
              },
              symbol: 'circle',
              symbolSize: 6,
            },
          ],
        },
      ],
    });

    return () => {
      chart.dispose();
      chartInstance.current = null;
    };
  }, [dimensions, hasData]);

  useEffect(() => {
    const el = chartRef.current;
    if (!el || !hasData) return;
    const observer = new ResizeObserver(() => chartInstance.current?.resize());
    observer.observe(el);
    return () => observer.disconnect();
  }, [hasData]);

  if (!hasData) {
    return <div className="chart-empty">暂无数据</div>;
  }

  return (
    <div className="radar-shell">
      <div className="radar-burst" aria-hidden="true" />
      <div
        ref={chartRef}
        className="radar-chart-canvas"
        role="img"
        aria-label="仓库健康度六维雷达图"
      />
    </div>
  );
}
