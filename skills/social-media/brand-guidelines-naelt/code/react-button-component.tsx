import React from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

export const NAELTButton: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  disabled = false,
  fullWidth = false,
  type = 'button',
}) => {
  const baseClasses = 'font-sans font-semibold rounded-md transition-all duration-base focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-primary-500 text-white hover:bg-primary-700 focus:ring-primary-500 disabled:bg-primary-300',
    secondary: 'bg-secondary-600 text-white hover:bg-secondary-700 focus:ring-secondary-500 disabled:bg-secondary-300',
    accent: 'bg-accent-500 text-white hover:bg-accent-600 focus:ring-accent-500 disabled:bg-accent-300',
    outline: 'bg-transparent border-2 border-primary-500 text-primary-500 hover:bg-primary-50 focus:ring-primary-500 disabled:border-primary-300 disabled:text-primary-300',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const widthClass = fullWidth ? 'w-full' : '';
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass}`;
  
  return (
    <button
      type={type}
      className={classes}
      onClick={onClick}
      disabled={disabled}
      aria-disabled={disabled}
    >
      {children}
    </button>
  );
};

// 使用範例
export const ButtonExamples = () => {
  return (
    <div className="space-y-4 p-8">
      <h2 className="text-2xl font-bold text-primary-600 mb-4">NAELT 按鈕範例</h2>
      
      {/* Primary Buttons */}
      <div className="space-x-2">
        <NAELTButton variant="primary" size="sm">小型主要按鈕</NAELTButton>
        <NAELTButton variant="primary" size="md">中型主要按鈕</NAELTButton>
        <NAELTButton variant="primary" size="lg">大型主要按鈕</NAELTButton>
      </div>
      
      {/* Secondary Buttons */}
      <div className="space-x-2">
        <NAELTButton variant="secondary" size="md">次要按鈕</NAELTButton>
        <NAELTButton variant="accent" size="md">強調按鈕</NAELTButton>
        <NAELTButton variant="outline" size="md">外框按鈕</NAELTButton>
      </div>
      
      {/* Disabled State */}
      <div className="space-x-2">
        <NAELTButton variant="primary" disabled>禁用狀態</NAELTButton>
      </div>
      
      {/* Full Width */}
      <div>
        <NAELTButton variant="primary" fullWidth>全寬按鈕</NAELTButton>
      </div>
      
      {/* With Icons */}
      <div className="space-x-2">
        <NAELTButton variant="primary">
          <span className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            立即捐款
          </span>
        </NAELTButton>
        
        <NAELTButton variant="accent">
          <span className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            加入志工
          </span>
        </NAELTButton>
      </div>
    </div>
  );
};

export default NAELTButton;
