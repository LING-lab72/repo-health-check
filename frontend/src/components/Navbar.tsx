import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { API_BASE } from '../api';
import { useApp } from '../context/AppContext';

interface GitHubUser {
  user_id: number;
  login: string;
  avatar_url: string;
}

export default function Navbar() {
  const { state, dispatch } = useApp();
  const isDark = state.theme === 'dark';
  const [user, setUser] = useState<GitHubUser | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/auth/me`)
      .then((r) => r.json())
      .then((json) => {
        if (json.code === 0 && json.data) setUser(json.data);
      })
      .catch(() => {});
  }, []);

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand">
          🏥 Repo Health Check
        </NavLink>
        <div className="navbar-links">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            首页
          </NavLink>
          <NavLink to="/leaderboard" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            排行榜
          </NavLink>
          <NavLink to="/compare" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            对比
          </NavLink>
          <NavLink to="/about" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            关于
          </NavLink>
          <button
            onClick={() => dispatch({ type: 'TOGGLE_THEME' })}
            className="theme-btn"
            title={isDark ? '切换浅色主题' : '切换深色主题'}
          >
            {isDark ? '☀️' : '🌙'}
          </button>
          {user ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--text-secondary)' }}>
              <img src={user.avatar_url} alt="" style={{ width: 20, height: 20, borderRadius: '50%' }} />
              {user.login}
            </span>
          ) : (
            <a href="/api/auth/github" className="nav-link">
              GitHub 登录
            </a>
          )}
          <a
            href="https://github.com/user/repo-health-check"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-link"
          >
            GitHub ↗
          </a>
        </div>
      </div>
    </nav>
  );
}
