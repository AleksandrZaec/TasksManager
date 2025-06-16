import clsx from 'clsx';
import s from './BackgroundImageLayout.module.scss';
import blob1 from '/images/blob1.png';
import blob2 from '/images/blob2.png';
import blob3 from '/images/blob3.png';
import { Outlet } from 'react-router-dom';

export const BackgroundImageLayout = () => {
  return (
    <div className={s.container}>
      <img src={blob1} className={clsx(s.backround, s.blob1)} />
      <img src={blob2} className={clsx(s.backround, s.blob2)} />
      <img src={blob3} className={clsx(s.backround, s.blob3)} />
      <div className={s.content}>
        <Outlet />
      </div>
    </div>
  );
};
