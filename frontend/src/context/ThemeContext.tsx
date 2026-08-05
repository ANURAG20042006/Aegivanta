import React, { createContext, ReactNode, useEffect, useMemo, useState } from 'react';

export type ThemeName = 'midnight' | 'aurora' | 'solar';

export interface ThemeOption {
  id: ThemeName;
  label: string;
  description: string;
  accent: string;
}

export const themeOptions: ThemeOption[] = [
  {
    id: 'midnight',
    label: 'Midnight',
    description: 'Deep contrast for long shifts',
    accent: '#00F0FF',
  },
  {
    id: 'aurora',
    label: 'Aurora',
    description: 'Teal glass with a softer glow',
    accent: '#5FF4C7',
  },
  {
    id: 'solar',
    label: 'Solar',
    description: 'Bright command-center mode',
    accent: '#0B76FF',
  },
];

interface ThemeContextType {
  theme: ThemeName;
  setTheme: (theme: ThemeName) => void;
  options: ThemeOption[];
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'sentinel_theme';

const getInitialTheme = (): ThemeName => {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'midnight' || stored === 'aurora' || stored === 'solar') {
    return stored;
  }
  return 'midnight';
};

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeName>(getInitialTheme);

  const setTheme = (nextTheme: ThemeName) => {
    setThemeState(nextTheme);
    localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  };

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme === 'solar' ? 'light' : 'dark';
  }, [theme]);

  useEffect(() => {
    const syncTheme = (event: StorageEvent) => {
      if (event.key === THEME_STORAGE_KEY && (event.newValue === 'midnight' || event.newValue === 'aurora' || event.newValue === 'solar')) {
        setThemeState(event.newValue);
      }
    };
    window.addEventListener('storage', syncTheme);
    return () => window.removeEventListener('storage', syncTheme);
  }, []);

  const value = useMemo(() => ({ theme, setTheme, options: themeOptions }), [theme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};
