import { forwardRef, TextareaHTMLAttributes } from 'react';
import clsx from 'clsx';
import s from './TextArea.module.scss';

type TextAreaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  extraClass?: string;
  errorText?: string;
};

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ extraClass, errorText, ...rest }, ref) => {
    return (
      <div className={clsx(s.container, extraClass)}>
        <textarea ref={ref} className={clsx(s.textarea, { [s.error]: !!errorText })} {...rest} />
        {errorText && <p className={s.errorText}>{errorText}</p>}
      </div>
    );
  },
);
