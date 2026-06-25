import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('UI error boundary caught an error', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="page-container fade-in" style={{ paddingTop: 80, textAlign: 'center' }}>
          <div className="glass-card" role="alert" style={{ maxWidth: 520, margin: '0 auto', padding: 36 }}>
            <h1 style={{ fontSize: 22, marginBottom: 12 }}>页面暂时无法显示</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 18 }}>
              请刷新页面重试，或返回首页重新开始分析。
            </p>
            <button className="btn" onClick={() => window.location.assign('/')}>
              返回首页
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
