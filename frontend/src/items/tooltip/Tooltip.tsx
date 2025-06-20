import { HTMLProps, PropsWithChildren } from 'react';
import clsx from 'clsx';

import s from './tooltip.module.scss';

type TooltipProps = PropsWithChildren<HTMLProps<HTMLInputElement>> & {
  error?: boolean;
  isVisible?: boolean;
  errorText?: string;
};

export const Tooltip = ({ error, isVisible, errorText }: TooltipProps) => {
  return (
    <div
      className={clsx(
        s.tooltip__popup,
        {
          [s.tooltip__popup__error]: error || errorText,
          [s.tooltip__popup__visible]: isVisible,
        },
        s.tooltip__popup__left,
      )}>
      {errorText && (
        <p className={clsx(s.tooltip__popup__error__text)}>
          <span className={s.tooltip__icon__alert}></span>
          {errorText}
        </p>
      )}
    </div>
  );
};
