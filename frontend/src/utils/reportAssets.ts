import type { AnalysisData, AnalysisDimension } from '../context/AppContext';

export interface LanguageDatum {
  label: string;
  value: number;
}

const LANGUAGE_LABELS: Record<string, string> = {
  python: 'Python',
  js_ts: 'JavaScript/TypeScript',
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  go: 'Go',
  rust: 'Rust',
  java: 'Java',
  other: 'Other',
};

const BADGE_COLORS: Record<string, string> = {
  brightgreen: '#22c55e',
  green: '#16a34a',
  yellowgreen: '#84cc16',
  yellow: '#eab308',
  orange: '#f97316',
  red: '#ef4444',
  blue: '#3b82f6',
  lightgrey: '#94a3b8',
};

export function normalizeBadgeColor(color: string | undefined): string {
  if (!color) return '#94a3b8';
  if (color.startsWith('#') || color.startsWith('rgb')) return color;
  return BADGE_COLORS[color] || color;
}

export function extractLanguageBreakdown(dimensions: AnalysisDimension[]): LanguageDatum[] {
  const codeQuality = dimensions.find((d) => d.dimension === 'code_quality');
  const details = codeQuality?.details || {};
  const raw = details.language_breakdown;
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return [];

  return Object.entries(raw as Record<string, unknown>)
    .map(([key, value]) => ({
      label: LANGUAGE_LABELS[key] || key.replace(/_/g, ' '),
      value: Number(value) || 0,
    }))
    .filter((item) => item.value > 0)
    .sort((a, b) => b.value - a.value);
}

export function getDominantLanguage(languages: LanguageDatum[]): string {
  return languages[0]?.label || 'open-source';
}

export function estimatePeerPercentile(score: number): number {
  return Math.max(1, Math.min(99, Math.round(score + 5)));
}

export async function openPdfPrintDialog(reportHtmlUrl: string): Promise<void> {
  void reportHtmlUrl;

  const report = document.querySelector<HTMLElement>('.report-page');
  if (!report) {
    window.print();
    return;
  }

  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import('html2canvas'),
    import('jspdf'),
  ]);

  const reportTitle = window.location.pathname
    .split('/')
    .filter(Boolean)
    .pop()
    ?.replace(/[^\w.-]+/g, '-');
  const fileName = `repo-health-report-${reportTitle || 'repository'}.pdf`;

  document.body.classList.add('pdf-exporting');
  await new Promise((resolve) => window.requestAnimationFrame(resolve));

  try {
    const canvas = await html2canvas(report, {
      backgroundColor: '#080e1c',
      scale: Math.min(2, window.devicePixelRatio || 1.5),
      useCORS: true,
      logging: false,
      ignoreElements: (element) =>
        element.classList.contains('report-actions') ||
        element.classList.contains('btn-back') ||
        element.classList.contains('dock-outer') ||
        element.classList.contains('dock-panel'),
    });

    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 8;
    const targetWidth = pageWidth - margin * 2;
    const targetHeight = pageHeight - margin * 2;
    const pxPerPage = Math.floor((targetHeight * canvas.width) / targetWidth);

    let sourceY = 0;
    let pageIndex = 0;
    while (sourceY < canvas.height) {
      const pageCanvas = document.createElement('canvas');
      const sliceHeight = Math.min(pxPerPage, canvas.height - sourceY);
      pageCanvas.width = canvas.width;
      pageCanvas.height = sliceHeight;
      const ctx = pageCanvas.getContext('2d');
      if (!ctx) break;

      ctx.fillStyle = '#080e1c';
      ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height);
      ctx.drawImage(
        canvas,
        0,
        sourceY,
        canvas.width,
        sliceHeight,
        0,
        0,
        pageCanvas.width,
        sliceHeight,
      );

      if (pageIndex > 0) pdf.addPage();
      const imageHeight = (sliceHeight * targetWidth) / canvas.width;
      pdf.addImage(pageCanvas.toDataURL('image/png'), 'PNG', margin, margin, targetWidth, imageHeight);
      sourceY += sliceHeight;
      pageIndex += 1;
    }

    pdf.save(fileName);
  } finally {
    document.body.classList.remove('pdf-exporting');
  }
}

function drawRoundedRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function fitText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string {
  if (ctx.measureText(text).width <= maxWidth) return text;
  let next = text;
  while (next.length > 4 && ctx.measureText(`${next}...`).width > maxWidth) {
    next = next.slice(0, -1);
  }
  return `${next}...`;
}

export function downloadShareCard(data: AnalysisData, languages: LanguageDatum[]): void {
  const canvas = document.createElement('canvas');
  canvas.width = 1200;
  canvas.height = 630;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const badgeColor = normalizeBadgeColor(data.badge_color);
  const dominantLanguage = getDominantLanguage(languages);
  const percentile = estimatePeerPercentile(data.health_score);
  const gradient = ctx.createLinearGradient(0, 0, 1200, 630);
  gradient.addColorStop(0, '#08111f');
  gradient.addColorStop(0.52, '#1f2937');
  gradient.addColorStop(1, '#0f766e');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 1200, 630);

  ctx.globalAlpha = 0.16;
  ctx.fillStyle = badgeColor;
  ctx.beginPath();
  ctx.arc(1040, 78, 230, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1;

  ctx.fillStyle = 'rgba(255,255,255,0.08)';
  drawRoundedRect(ctx, 54, 54, 1092, 522, 32);
  ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.16)';
  ctx.lineWidth = 2;
  ctx.stroke();

  const repoName = data.repo_url.replace(/^https?:\/\/github\.com\//, '');
  ctx.fillStyle = '#cbd5e1';
  ctx.font = '600 28px "Segoe UI", sans-serif';
  ctx.fillText('Repo Health Check Wrapped', 94, 118);

  ctx.fillStyle = '#ffffff';
  ctx.font = '800 44px "Segoe UI", sans-serif';
  ctx.fillText(fitText(ctx, repoName, 720), 94, 186);

  ctx.fillStyle = '#99f6e4';
  ctx.font = '700 28px "Segoe UI", sans-serif';
  ctx.fillText(`超过 ${percentile}% 的 ${dominantLanguage} 项目`, 94, 232);

  ctx.font = '900 132px "Segoe UI", sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(Math.round(data.health_score)), 94, 370);
  ctx.font = '700 34px "Segoe UI", sans-serif';
  ctx.fillStyle = '#cbd5e1';
  ctx.fillText('/100', 258, 363);

  ctx.fillStyle = badgeColor;
  drawRoundedRect(ctx, 94, 402, 168, 54, 18);
  ctx.fill();
  ctx.fillStyle = '#ffffff';
  ctx.font = '800 28px "Segoe UI", sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(data.badge_level, 178, 438);
  ctx.textAlign = 'left';

  const radar = data.dimensions.slice(0, 8);
  const cx = 840;
  const cy = 292;
  const radius = 142;
  if (radar.length >= 3) {
    ctx.strokeStyle = 'rgba(203,213,225,0.24)';
    ctx.lineWidth = 2;
    for (const ring of [0.25, 0.5, 0.75, 1]) {
      ctx.beginPath();
      radar.forEach((_, i) => {
        const angle = -Math.PI / 2 + (Math.PI * 2 * i) / radar.length;
        const x = cx + Math.cos(angle) * radius * ring;
        const y = cy + Math.sin(angle) * radius * ring;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.stroke();
    }
    ctx.beginPath();
    radar.forEach((dim, i) => {
      const angle = -Math.PI / 2 + (Math.PI * 2 * i) / radar.length;
      const scoreRadius = radius * Math.max(0, Math.min(100, dim.score)) / 100;
      const x = cx + Math.cos(angle) * scoreRadius;
      const y = cy + Math.sin(angle) * scoreRadius;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(45,212,191,0.24)';
    ctx.strokeStyle = '#2dd4bf';
    ctx.lineWidth = 4;
    ctx.fill();
    ctx.stroke();
  }

  ctx.fillStyle = '#cbd5e1';
  ctx.font = '600 22px "Segoe UI", sans-serif';
  ctx.fillText('Language Mix', 94, 488);
  let x = 94;
  languages.slice(0, 4).forEach((lang) => {
    const text = `${lang.label} ${lang.value}`;
    ctx.fillStyle = '#e2e8f0';
    ctx.font = '700 20px "Segoe UI", sans-serif';
    ctx.fillText(text, x, 526);
    x += Math.max(160, ctx.measureText(text).width + 32);
  });

  const link = document.createElement('a');
  link.download = `${repoName.replace(/[^\w.-]+/g, '-')}-repo-health-card.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}
