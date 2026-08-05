import React, { useState } from 'react';
import { Check, Palette, Sparkles } from 'lucide-react';
import { ThemeName } from '../../context/ThemeContext';
import { useTheme } from '../../hooks/useTheme';

export const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme, options } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const activeTheme = options.find((option) => option.id === theme) || options[0];

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        aria-label="Change interface theme"
        aria-expanded={isOpen}
        className="theme-control"
      >
        <Palette className="w-4 h-4" />
        <span className="hidden lg:inline">{activeTheme.label}</span>
        <span className="theme-swatch" style={{ backgroundColor: activeTheme.accent }} />
      </button>

      {isOpen && (
        <>
          <button type="button" aria-label="Close theme menu" className="fixed inset-0 z-40 cursor-default" onClick={() => setIsOpen(false)} />
          <div className="theme-menu" role="menu">
            <div className="theme-menu-heading">
              <Sparkles className="w-3.5 h-3.5" />
              <span>LIVE VISUAL PROFILE</span>
            </div>
            {options.map((option) => (
              <button
                key={option.id}
                type="button"
                role="menuitem"
                onClick={() => {
                  setTheme(option.id as ThemeName);
                  setIsOpen(false);
                }}
                className={`theme-option ${theme === option.id ? 'is-active' : ''}`}
              >
                <span className="theme-swatch" style={{ backgroundColor: option.accent }} />
                <span className="flex-1 text-left">
                  <span className="block text-xs font-semibold">{option.label}</span>
                  <span className="block text-[10px] opacity-60">{option.description}</span>
                </span>
                {theme === option.id && <Check className="w-4 h-4" />}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
