import { Block } from '../../block/Block';
import { FormField } from '../../form-field/FormField';
import s from '../../../components/setting/Setting.module.scss';
import { validation } from '../../form-field/validation';
import { Button } from '../../button/Button';
import { useForm } from 'react-hook-form';

type FormValues = {
  password: string;
  repeat_password: string;
};

export const PasswordSetting = () => {
  const {
    control,
    formState: { errors },
    handleSubmit,
    clearErrors,
    watch,
  } = useForm<FormValues>({
    mode: 'onSubmit',
  });
  const onSubmit = (data: FormValues) => {
    console.log(data);
  };
  const handleInputInteraction = () => {
    clearErrors();
  };
  const passwordWatch = watch('password');

  return (
    <Block extraClass={s.block}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
        <FormField
          name='password'
          control={control}
          placeholder={'Введите пароль'}
          type={'password'}
          label={'Пароль'}
          rules={validation().password}
          error={Boolean(errors.password)}
          errorText={errors.password?.message}
          onChange={handleInputInteraction}
          onBlur={handleInputInteraction}
          extraClass={s.input}
        />
        <FormField
          name='repeat_password'
          control={control}
          placeholder='Повторите пароль'
          type='password'
          label='Повторите пароль'
          rules={validation(passwordWatch).repeat_password}
          error={Boolean(errors.repeat_password)}
          errorText={errors.repeat_password?.message}
          onChange={handleInputInteraction}
          onBlur={handleInputInteraction}
          extraClass={s.input}
        />
        <Button type={'outline'}>Сохранить</Button>
      </form>
    </Block>
  );
};
