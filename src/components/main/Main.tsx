import { Block } from '../../items/block/Block';
import { Button } from '../../items/button/Button';
import { Header } from '../header/Header';
import s from './Main.module.scss';

export const Main = () => {
  return (
    <Header>
      <div className={s.content}>
        <div className={s.main}>
          <h1>Название проекта</h1>
          <p>Участников: 10</p>
        </div>
        <div className={s.main}>
          <p>Список задач</p>
        </div>
        <div className={s.table}>
          <Block>
            <h1>Ожидает</h1>
            <div></div>
            <Button>Добавить задачу</Button>
          </Block>
          <Block>
            <h1>В разработке</h1>
            <Button>Добавить задачу</Button>
          </Block>
          <Block>
            <h1>Готово</h1>
            <Button>Добавить задачу</Button>
          </Block>
        </div>
      </div>
    </Header>
  );
};
