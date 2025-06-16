import { forwardRef, useState } from 'react';
import s from './Input.module.scss';
import clsx from 'clsx';
import closeEye from '/icons/close_eye.png';
import openEye from '/icons/open_eye.png';
type InputProps = {
  label: string;
  placeholder: string;
  type: 'email' | 'password';
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: () => void;
  error?: boolean;
};
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, placeholder, type, onChange, onBlur, error = false, ...rest }, ref) => {
    const [showIcon, setShowIcons] = useState(false);
    const typePassword = type === 'password';
    const currentType = typePassword && showIcon ? 'text' : type;

    return (
      <div className={s.field}>
        <p className={s.title}>{label}</p>
        <input
          type={currentType}
          placeholder={placeholder}
          ref={ref}
          {...rest}
          className={clsx(s.input, { [s.input__error]: error })}
          onChange={onChange}
          onBlur={onBlur}
        />
        {typePassword && (
          <div className={s.icon} onClick={() => setShowIcons((prev) => !prev)}>
            <img src={showIcon ? openEye : closeEye} alt='icon' className={s.icon} />
          </div>
        )}
      </div>
    );
  },
);
