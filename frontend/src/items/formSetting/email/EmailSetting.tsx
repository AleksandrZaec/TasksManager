import { Block } from '../../block/Block';
import { FormField } from '../../form-field/FormField';
import s from '../../../components/setting/Setting.module.scss';
import { validation } from '../../form-field/validation';
import { Button } from '../../button/Button';
import { useForm } from 'react-hook-form';

type FormValues = {
  email: string;
};

export const EmailSetting = () => {
  const {
    control,
    formState: { errors },
    handleSubmit,
    clearErrors,
  } = useForm<FormValues>({
    mode: 'onSubmit',
  });
  const onSubmit = (data: FormValues) => {
    console.log(data);
  };
  const handleInputInteraction = () => {
    clearErrors();
  };
  return (
    <Block extraClass={s.block}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
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
          onBlur={handleInputInteraction}
          extraClass={s.input}
        />
        <Button type={'outline'}>Сохранить</Button>
      </form>
    </Block>
  );
};
