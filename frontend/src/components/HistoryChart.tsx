import { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([LineChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer]);

interface HistoryEntry {
  analyzed_at: string;
  health_score: number;
  badge_level: string;
}

interface Props {
  history: HistoryEntry[];
}

export default function HistoryChart({ history }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || history.length < 2) return;
    const chart = echarts.init(chartRef.current);
    chartInstance.current = chart;

    const dates = history.map((h) => {
      const d = new Date(h.analyzed_at);
      return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
    });
    const scores = history.map((h) => h.health_score);

    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 20, right: 20, bottom: 30, left: 40 },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } },
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } },
      },
      series: [
        {
          type: 'line',
          data: scores,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { color: '#6366f1', width: 2 },
          itemStyle: { color: '#6366f1' },
          areaStyle: { color: 'rgba(99,102,241,0.1)' },
          markLine: {
            silent: true,
            data: [
              { yAxis: 80, lineStyle: { color: '#22c55e', type: 'dashed' }, label: { formatter: 'A', color: '#22c55e' } },
              { yAxis: 60, lineStyle: { color: '#eab308', type: 'dashed' }, label: { formatter: 'B', color: '#eab308' } },
            ],
          },
        },
      ],
    });

    return () => {
      chart.dispose();
      chartInstance.current = null;
    };
  }, [history]);

  // Resize on container or window resize
  useEffect(() => {
    const el = chartRef.current;
    if (!el) return;
    const observer = new ResizeObserver(() => chartInstance.current?.resize());
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div style={{ marginBottom: 24 }}>
      <h2 className="section-title">历史趋势</h2>
      <div className="card">
        <div ref={chartRef} style={{ width: '100%', height: 250 }} />
      </div>
    </div>
  );
}
