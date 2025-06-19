export const validation = (passwordValue?: string) => ({
  email: {
    required: 'Это поле обязательно',
    pattern: {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: 'Некорректный формат email',
    },
  },
  password: {
    required: 'Это поле обязательно',
  },
  repeat_password: {
    required: 'Это поле обязательно',
    validate: (value: string) => value === passwordValue || 'Пароли не совпадают',
  },
  first_name: { required: 'Имя обязательно' },
  last_name: { required: 'Фамилия обязательна' },
});
