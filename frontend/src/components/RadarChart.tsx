import { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { RadarChart as ERadarChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent } from 'echarts/components';
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

  if (!dimensions || dimensions.length === 0) {
    return <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-secondary)' }}>暂无数据</div>;
  }

  useEffect(() => {
    if (!chartRef.current) return;
    const chart = echarts.init(chartRef.current);
    chartInstance.current = chart;

    chart.setOption({
      tooltip: { trigger: 'item' },
      radar: {
        center: ['50%', '50%'],
        radius: '70%',
        indicator: dimensions.map((d) => ({
          name: d.name,
          max: 100,
        })),
        axisName: { color: '#94a3b8', fontSize: 12 },
        splitArea: {
          areaStyle: { color: ['rgba(99,102,241,0.05)', 'rgba(99,102,241,0.1)'] },
        },
        splitLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } },
        axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: dimensions.map((d) => d.score),
              name: '健康度',
              areaStyle: { color: 'rgba(99,102,241,0.25)' },
              lineStyle: { color: '#6366f1', width: 2 },
              itemStyle: { color: '#6366f1' },
            },
          ],
        },
      ],
    });

    return () => {
      chart.dispose();
      chartInstance.current = null;
    };
  }, [dimensions]);

  // Resize on container or window resize
  useEffect(() => {
    const el = chartRef.current;
    if (!el) return;
    const observer = new ResizeObserver(() => chartInstance.current?.resize());
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return <div ref={chartRef} style={{ width: '100%', height: 400 }} />;
}
