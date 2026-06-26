import { createContext, useContext, useEffect, useReducer, type Dispatch, type ReactNode } from 'react';

export interface AnalysisDimension {
  dimension: string;
  score: number;
  details: Record<string, unknown>;
  issues: string[];
}

export interface AIDiagnosisItem {
  advice: string;
  severity: 'high' | 'medium' | 'low';
  estimated_hours: number;
  confidence: number;
  need_human_review: boolean;
  provider?: string;
}

export interface AnalysisData {
  repo_url: string;
  health_score: number;
  badge_level: string;
  badge_color: string;
  badge_description: string;
  dimensions: AnalysisDimension[];
  ai_diagnosis: AIDiagnosisItem[];
  ai_provider?: string;
  analyzed_at: string;
}

interface AppState {
  status: 'idle' | 'loading' | 'success' | 'error';
  analysisResult: AnalysisData | null;
  error: string | null;
  theme: 'dark' | 'light';
}

type AppAction =
  | { type: 'START_ANALYSIS' }
  | { type: 'ANALYSIS_SUCCESS'; payload: AnalysisData }
  | { type: 'ANALYSIS_ERROR'; payload: string }
  | { type: 'RESET' }
  | { type: 'TOGGLE_THEME' };

function getSavedTheme(): 'dark' | 'light' {
  try {
    const saved = localStorage.getItem('theme');
    if (saved === 'light') return 'light';
  } catch {
    // localStorage can be unavailable in private browsing or tests.
  }
  return 'dark';
}

const initialState: AppState = {
  status: 'idle',
  analysisResult: null,
  error: null,
  theme: getSavedTheme(),
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'START_ANALYSIS':
      return { ...state, status: 'loading', analysisResult: null, error: null };
    case 'ANALYSIS_SUCCESS':
      return { ...state, status: 'success', analysisResult: action.payload };
    case 'ANALYSIS_ERROR':
      return { ...state, status: 'error', error: action.payload };
    case 'TOGGLE_THEME': {
      const next = state.theme === 'dark' ? 'light' : 'dark';
      try {
        localStorage.setItem('theme', next);
      } catch {
        // Theme still changes in memory when persistence is unavailable.
      }
      return { ...state, theme: next };
    }
    case 'RESET':
      return { ...initialState, theme: state.theme };
    default:
      return state;
  }
}

interface AppContextValue {
  state: AppState;
  dispatch: Dispatch<AppAction>;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', state.theme);
  }, [state.theme]);

  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useApp(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
