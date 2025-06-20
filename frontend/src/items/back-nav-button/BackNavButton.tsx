import { useNavigate } from 'react-router-dom';
import s from './BackNavButton.module.scss';

export const BackNavButton = () => {
  const navigate = useNavigate();
  const handleBack = () => {
    navigate(-1);
  };
  return (
    <div className={s.container}>
      <p className={s.button} onClick={handleBack}>
        {'< Назад'}
      </p>
    </div>
  );
};
