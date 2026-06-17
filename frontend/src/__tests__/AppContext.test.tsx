import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { AppProvider, useApp } from '../context/AppContext';

describe('AppContext', () => {
  it('should start with idle status', () => {
    const { result } = renderHook(() => useApp(), { wrapper: AppProvider });

    expect(result.current.state.status).toBe('idle');
    expect(result.current.state.analysisResult).toBeNull();
    expect(result.current.state.error).toBeNull();
  });

  it('should transition idle → loading on START_ANALYSIS', () => {
    const { result } = renderHook(() => useApp(), { wrapper: AppProvider });

    act(() => {
      result.current.dispatch({ type: 'START_ANALYSIS' });
    });

    expect(result.current.state.status).toBe('loading');
  });

  it('should transition loading → success on ANALYSIS_SUCCESS', () => {
    const { result } = renderHook(() => useApp(), { wrapper: AppProvider });

    act(() => {
      result.current.dispatch({ type: 'START_ANALYSIS' });
    });

    const mockData = {
      repo_url: 'https://github.com/test/repo',
      health_score: 85.0,
      badge_level: 'A',
      badge_color: 'brightgreen',
      badge_description: '健康',
      dimensions: [{ dimension: 'code_quality', score: 85, details: {}, issues: [] }],
      ai_diagnosis: [],
      analyzed_at: '2026-01-01T00:00:00Z',
    };

    act(() => {
      result.current.dispatch({ type: 'ANALYSIS_SUCCESS', payload: mockData });
    });

    expect(result.current.state.status).toBe('success');
    expect(result.current.state.analysisResult).toEqual(mockData);
    expect(result.current.state.error).toBeNull();
  });

  it('should transition loading → error on ANALYSIS_ERROR', () => {
    const { result } = renderHook(() => useApp(), { wrapper: AppProvider });

    act(() => {
      result.current.dispatch({ type: 'START_ANALYSIS' });
    });
    act(() => {
      result.current.dispatch({ type: 'ANALYSIS_ERROR', payload: 'Network error' });
    });

    expect(result.current.state.status).toBe('error');
    expect(result.current.state.error).toBe('Network error');
    expect(result.current.state.analysisResult).toBeNull();
  });

  it('should reset to initial state on RESET', () => {
    const { result } = renderHook(() => useApp(), { wrapper: AppProvider });

    act(() => {
      result.current.dispatch({ type: 'START_ANALYSIS' });
    });
    act(() => {
      result.current.dispatch({ type: 'ANALYSIS_ERROR', payload: 'Error' });
    });
    act(() => {
      result.current.dispatch({ type: 'RESET' });
    });

    expect(result.current.state.status).toBe('idle');
    expect(result.current.state.analysisResult).toBeNull();
    expect(result.current.state.error).toBeNull();
  });
});
