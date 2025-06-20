import { Block } from '@items/block/Block';
import { FormField } from '@items/form-field/FormField';
import s from '@components/setting/Setting.module.scss';
import { validation } from '@items/form-field/validation';
import { Button } from '@items/button/Button';
import { useForm } from 'react-hook-form';

type FormValues = {
  first_name: string;
};

export const FirstNameSetting = () => {
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
          name='first_name'
          control={control}
          placeholder={'Введите имя'}
          type={'text'}
          label={'Имя'}
          rules={validation().first_name}
          error={Boolean(errors.first_name)}
          errorText={errors.first_name?.message}
          onChange={handleInputInteraction}
          onBlur={handleInputInteraction}
          extraClass={s.input}
        />
        <Button type={'outline'}>Сохранить</Button>
      </form>
    </Block>
  );
};
