import { Block } from '../../items/block/Block';
import { Button } from '../../items/button/Button';
import { Input } from '../../items/input/Input';
import s from './Setting.module.scss';

export const Setting = () => {
  return (
    <div>
      <p className={s.title}>Изменить личные данные</p>
      <div className={s.container}>
        <Block extraClass={s.block}>
          <form>
            <Input
              extraClass={s.input}
              label={'Фамилия'}
              placeholder='Иванов'
              type={'text'}
              onChange={() => {}}
            />
            <Button type={'outline'}>Сохранить</Button>
          </form>
        </Block>
        <Block extraClass={s.block}>
          <form>
            <Input
              extraClass={s.input}
              label={'Имя'}
              placeholder='Иван'
              type={'text'}
              onChange={() => {}}
            />
            <Button type={'outline'}>Сохранить</Button>
          </form>
        </Block>
        <Block extraClass={s.block}>
          <form>
            <Input
              extraClass={s.input}
              label={'Пароль'}
              placeholder='Введите пароль'
              type={'password'}
              onChange={() => {}}
            />
            <Input
              extraClass={s.input}
              label={'Повторите пароль'}
              placeholder='Повторите пароль'
              type={'password'}
              onChange={() => {}}
            />
            <Button type={'outline'}>Сохранить</Button>
          </form>
        </Block>
        <Block extraClass={s.block}>
          <form>
            <Input
              extraClass={s.input}
              label={'Почта'}
              placeholder='Введите почту'
              type={'email'}
              onChange={() => {}}
            />
            <Button type={'outline'}>Сохранить</Button>
          </form>
        </Block>
      </div>
    </div>
  );
};
