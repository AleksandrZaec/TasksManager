import React from 'react';
import s from './Button.module.scss';
import clsx from 'clsx';

type ButtonProps = {
  children: React.ReactNode;
  type: 'outline' | 'text' | 'dropdown';
  extraClass?: string;
  icon?: boolean;
  chevron?: 'up' | 'down';
  onClick?: () => void;
};
export const Button = ({ children, type, extraClass, icon, chevron, onClick }: ButtonProps) => {
  return (
    <button className={clsx(s.button, s[`button__${type}`], extraClass)} onClick={onClick}>
      {icon && <img className={s.icon} src='/icons/plus.png' alt='plus' />}
      {chevron && (
        <img
          className={s.chevron}
          src={chevron === 'up' ? '/icons/chevron-up.png' : '/icons/chevron-down.png'}
          alt='chervon'
        />
      )}
      {children}
    </button>
  );
};
