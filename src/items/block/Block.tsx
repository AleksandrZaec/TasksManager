import s from './block.module.scss';
import clsx from 'clsx';

type BgContainerProps = {
  children: React.ReactNode;
  extraClass?: string;
};

export const Block = ({ children, extraClass }: BgContainerProps) => {
  return <div className={clsx(s.block, extraClass)}>{children}</div>;
};
