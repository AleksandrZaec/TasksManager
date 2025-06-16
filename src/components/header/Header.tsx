import { Block } from '../../items/block/Block';
import s from './Header.module.scss';

type HeaderProps = {
  children: React.ReactNode;
};
export const Header = ({ children }: HeaderProps) => {
  return (
    <div className={s.container}>
      <div className={s.menu}>
        <Block extraClass={s.header}>
          <p>Проекты(комнаты)</p>
          <p>Календарь</p>
          <p>Встречи</p>
          <p>Профиль</p>
        </Block>
        {children}
      </div>
    </div>
  );
};
