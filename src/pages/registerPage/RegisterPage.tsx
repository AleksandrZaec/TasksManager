import s from '../loginPage/LoginPage.module.scss';
import woman from '/images/woman.png';
import { Register } from '../../components/register/Register';

export const RegisterPage = () => {
  return (
    <div className={s.container}>
      <div className={s.main}>
        <div className={s.left}>
          <img src={woman} alt='woman_with_laptop' />
        </div>
        <div className={s.right}>
          <Register />
        </div>
      </div>
    </div>
  );
};
