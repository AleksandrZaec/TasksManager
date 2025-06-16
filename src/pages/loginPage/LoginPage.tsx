import s from './LoginPage.module.scss';
import man from '/images/man.png';
import { Login } from '../../components/login/Login';
export const LoginPage = () => {
  return (
    <div className={s.container}>
      <div className={s.main}>
        <div className={s.left}>
          <img src={man} alt='man_with_laptop' />
        </div>
        <div className={s.right}>
          <Login />
        </div>
      </div>
    </div>
  );
};
