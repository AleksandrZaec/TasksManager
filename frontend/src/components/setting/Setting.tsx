import { EmailSetting } from '@items/formSetting/email/EmailSetting';
import { FirstNameSetting } from '@items/formSetting/first-name/FirstNameSetting';
import { LastNameSetting } from '@items/formSetting/last-name/LastNameSetting';
import { PasswordSetting } from '@items/formSetting/password/PasswordSetting';
import s from './Setting.module.scss';

export const Setting = () => {
  return (
    <div>
      <p className={s.title}>Изменить личные данные</p>
      <div className={s.container}>
        <LastNameSetting />
        <FirstNameSetting />
        <PasswordSetting />
        <EmailSetting />
      </div>
    </div>
  );
};
