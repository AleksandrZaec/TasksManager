import React from 'react';
import s from './Button.module.scss';
import clsx from 'clsx';

type ButtonProps = {
  children: React.ReactNode;
  type: 'outline' | 'text';
  extraClass?: string;
  icon?: boolean;
};
export const Button = ({ children, type, extraClass, icon }: ButtonProps) => {
  return (
    <button className={clsx(s.button, s[`button__${type}`], extraClass)}>
      {icon && <img className={s.icon} src='/icons/plus.png' alt='plus' />}
      {children}
    </button>
  );
};
