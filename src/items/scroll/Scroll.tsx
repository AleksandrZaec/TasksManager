import clsx from 'clsx';
import s from './scroll.module.scss';
import { forwardRef, ReactNode } from 'react';

type ScrollProps = {
  className?: string;
  children: ReactNode;
};
export const Scroll = forwardRef<HTMLDivElement, ScrollProps>(({ className, children }, ref) => {
  return (
    <div className={s.scrollBox}>
      <div className={clsx(s.scroll, className)} ref={ref}>
        {children}
      </div>
    </div>
  );
});

// Добавляем displayName для ESLint
// Scroll.displayName = 'Scroll';
