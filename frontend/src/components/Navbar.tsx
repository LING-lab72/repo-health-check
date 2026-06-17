import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { API_BASE } from '../api';
import { useApp } from '../context/AppContext';
import Dock from './Dock';

interface GitHubUser {
  user_id: number;
  login: string;
  avatar_url: string;
}

/* Simple inline SVG icons — no external icon library needed */
function HomeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function TrophyIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" />
      <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />
      <path d="M4 22h16" />
      <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20 7 22" />
      <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20 17 22" />
      <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
    </svg>
  );
}

function CompareIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="8" height="18" rx="2" />
      <rect x="14" y="3" width="8" height="18" rx="2" />
      <line x1="6" y1="9" x2="6" y2="9.01" />
      <line x1="18" y1="9" x2="18" y2="9.01" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  );
}

function ThemeIcon({ isDark }: { isDark: boolean }) {
  return isDark ? (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

function GitHubIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-3.99-1.455-.135-.345-.72-1.455-1.23-1.755-.42-.225-1.02-.78.015-.795.975-.015 1.65.9 1.875 1.275 1.08 1.815 2.79 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.275-3.225-.135-.3-.57-1.53.135-3.18 0 0 1.05-.345 3.45 1.23 1.005-.285 2.07-.42 3.135-.42s2.13.135 3.135.42c2.4-1.575 3.45-1.23 3.45-1.23.705 1.65.265 2.88.135 3.18.81.84 1.275 1.905 1.275 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
    </svg>
  );
}

export default function Navbar() {
  const { state, dispatch } = useApp();
  const isDark = state.theme === 'dark';
  const [user, setUser] = useState<GitHubUser | null>(null);
  const location = useLocation();

  useEffect(() => {
    fetch(`${API_BASE}/api/auth/me`)
      .then((r) => r.json())
      .then((json) => {
        if (json.code === 0 && json.data) setUser(json.data);
      })
      .catch(() => {});
  }, []);

  const dockItems = [
    {
      icon: <HomeIcon />,
      label: '首页',
      onClick: () => window.location.href = '/',
      className: location.pathname === '/' ? 'active' : '',
    },
    {
      icon: <TrophyIcon />,
      label: '排行榜',
      onClick: () => window.location.href = '/leaderboard',
      className: location.pathname === '/leaderboard' ? 'active' : '',
    },
    {
      icon: <CompareIcon />,
      label: '对比',
      onClick: () => window.location.href = '/compare',
      className: location.pathname === '/compare' ? 'active' : '',
    },
    {
      icon: <InfoIcon />,
      label: '关于',
      onClick: () => window.location.href = '/about',
      className: location.pathname === '/about' ? 'active' : '',
    },
    {
      icon: <ThemeIcon isDark={isDark} />,
      label: isDark ? '浅色模式' : '深色模式',
      onClick: () => dispatch({ type: 'TOGGLE_THEME' }),
      className: '',
    },
    {
      icon: <GitHubIcon />,
      label: 'GitHub',
      onClick: () => window.open('https://github.com/LING-lab72/repo-health-check', '_blank'),
      className: '',
    },
    ...(user
      ? [
          {
            icon: <img src={user.avatar_url} alt={user.login} className="dock-avatar" />,
            label: user.login,
            onClick: () => {},
            className: '',
          },
        ]
      : [
          {
            icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>,
            label: 'GitHub 登录',
            onClick: () => window.location.href = '/api/auth/github',
            className: '',
          },
        ]),
  ];

  return <Dock items={dockItems} />;
}
