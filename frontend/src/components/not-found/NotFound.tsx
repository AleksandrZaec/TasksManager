import { useNavigate } from 'react-router-dom';
import { Block } from '@items/block/Block';
import s from './NotFound.module.scss';
import { ROUTES } from '@route/Routes';

export const NotFound = () => {
  const navigate = useNavigate();
  const handleLogin = () => {
    navigate(ROUTES.LOGIN);
  };
  return (
    <div className={s.container}>
      <Block extraClass={s.block}>
        <h1 className={s.title}>Страница не найдена</h1>
        <p onClick={handleLogin} className={s.subTitle}>Вернуться на главную страницу</p>
      </Block>
    </div>
  );
};
