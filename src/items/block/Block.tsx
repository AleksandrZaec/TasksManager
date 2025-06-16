import s from './block.module.scss';
import clsx from 'clsx';

type BlockProps = {
  children: React.ReactNode;
  extraClass?: string;
};

export const Block = ({ children, extraClass }: BlockProps) => {
  return <div className={clsx(s.block, extraClass)}>{children}</div>;
};
