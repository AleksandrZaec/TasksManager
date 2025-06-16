import clsx from 'clsx';
import s from './scroll.module.scss';
import { forwardRef, ReactNode } from 'react';

type ScrollProps = {
  extraClass?: string;
  children: ReactNode;
};
export const Scroll = forwardRef<HTMLDivElement, ScrollProps>(({ extraClass, children }, ref) => {
  return (
    <div className={s.scrollBox}>
      <div className={clsx(s.scroll, extraClass)} ref={ref}>
        {children}
      </div>
    </div>
  );
});

// Добавляем displayName для ESLint
// Scroll.displayName = 'Scroll';
