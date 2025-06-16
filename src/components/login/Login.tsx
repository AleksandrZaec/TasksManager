import { useForm } from 'react-hook-form';
import { FormField } from '../../items/form-field/FormField';
import s from './Login.module.scss';
import { useEffect, useState } from 'react';
import { validation } from '../../items/form-field/validation';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../../route/Routes';
import { Button } from '../../items/button/Button';

type FormValues = {
  email: string;
  password: string;
};
export const Login = () => {
  const [showTooltip, setShowTooltip] = useState(false);
  const {
    control,
    formState: { errors },
    handleSubmit,
    clearErrors,
    trigger,
    watch,
  } = useForm<FormValues>({
    mode: 'onSubmit',
  });

  const navigate = useNavigate();

  const onSubmit = async (data: FormValues) => {
    const valid = await trigger();
    if (valid) {
      console.log(data);
      setShowTooltip(false);
    } else {
      setShowTooltip(true);
    }
  };

  const handleInputInteraction = () => {
    clearErrors();
    setShowTooltip(false);
  };

  const handleNavRegister = () => {
    navigate(ROUTES.REGISTER);
  };

  const mailWatch = watch('email');
  useEffect(() => {
    if (mailWatch) {
      setShowTooltip(false);
    }
  }, [mailWatch, showTooltip]);

  return (
    <form noValidate className={s.form} onSubmit={handleSubmit(onSubmit)}>
      <div className={s.container}>
        <h1 className={s.title}>Вход</h1>
        <FormField
          name='email'
          control={control}
          placeholder='Введите почту'
          type='email'
          label='Адрес электронной почты'
          rules={validation().email}
          error={Boolean(errors.email)}
          errorText={errors.email?.message}
          onChange={handleInputInteraction}
          showTooltip={showTooltip}
          onBlur={handleInputInteraction}
        />
        <FormField
          name='password'
          control={control}
          placeholder='Введите пароль'
          type='password'
          label='Пароль'
          rules={validation().password}
          error={Boolean(errors.password)}
          errorText={errors.password?.message}
          onChange={handleInputInteraction}
          showTooltip={showTooltip}
          onBlur={handleInputInteraction}
        />
        <Button>Войти</Button>
        <p className={s.title__sub}>
          Нет личного кабинета? Тогда{' '}
          <span className={s.title__sub__reg} onClick={handleNavRegister}>
            зарегистрируйтесь
          </span>
          .
        </p>
      </div>
    </form>
  );
};
