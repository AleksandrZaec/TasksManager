import { Block } from '../../block/Block';
import { FormField } from '../../form-field/FormField';
import s from '../../../components/setting/Setting.module.scss';
import { validation } from '../../form-field/validation';
import { Button } from '../../button/Button';
import { useForm } from 'react-hook-form';

type FormValues = {
  last_name: string;
};

export const LastNameSetting = () => {
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
          name='last_name'
          control={control}
          placeholder={'Введите фамилию'}
          type={'text'}
          label={'Фамилия'}
          rules={validation().last_name}
          error={Boolean(errors.last_name)}
          errorText={errors.last_name?.message}
          onChange={handleInputInteraction}
          onBlur={handleInputInteraction}
          extraClass={s.input}
        />
        <Button type={'outline'}>Сохранить</Button>
      </form>
    </Block>
  );
};
