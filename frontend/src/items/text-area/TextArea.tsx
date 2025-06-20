import { forwardRef, TextareaHTMLAttributes } from 'react';
import clsx from 'clsx';
import s from './TextArea.module.scss';

type TextAreaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  extraName?: string;
  errorText?: string;
};

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ extraName, errorText, ...rest }, ref) => {
    return (
      <div className={clsx(s.container, extraName)}>
        <textarea ref={ref} className={clsx(s.textarea, { [s.error]: !!errorText })} {...rest} />
        {errorText && <p className={s.errorText}>{errorText}</p>}
      </div>
    );
  },
);
