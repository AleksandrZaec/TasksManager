import { useState } from 'react';
import { Header } from '../header/Header';
import s from './Profile.module.scss';
import style from '../main/Main.module.scss';
import { Block } from '@items/block/Block';
import { Button } from '@items/button/Button';
import { mockData } from '@utils/mockData';
import { TasksUser } from '@items/tasks-user/TasksUser';
import { Outlet, useNavigate } from 'react-router-dom';
import { ROUTES } from '@route/Routes';
import { BackNavButton } from '@items/back-nav-button/BackNavButton';

export const Profile = () => {
  const [selectedTeam, setSelectedTeam] = useState<string>('Team1');
  const currentName = 'Иванов';
  const currentExecutorr = mockData.filter((item) => item.executor === currentName);
  const navigate = useNavigate();
  const handleSetting = () => {
    navigate(ROUTES.SETTING);
  };
  return (
    <Header setSelectedTeam={setSelectedTeam} selectedTeam={selectedTeam}>
      <BackNavButton />
      <div className={s.container}>
        <div className={s.blockData}>
          <Block extraClass={s.blockUser}>
            <h1 className={s.title}>
              {'Иванов Очень длинное слово которое может быть перенесено.'}
            </h1>
            <p className={s.subTitle}>ID</p>
            {selectedTeam && <p className={s.subTitle}>Роль в {selectedTeam}</p>}
            <p className={s.subTitle}>
              {'ivanov1111111111111111111111111444444444444444444444111111@mail.ru'}
            </p>
            {location.pathname === '/profile' && (
              <div className={s.button}>
                <Button type={'outline'} onClick={handleSetting}>
                  Редактировать
                </Button>
              </div>
            )}
          </Block>
          <Block extraClass={s.blockStar}>
            <img src='/icons/star.webp' alt='star' className={s.icon} />
            <div className={s.star}>
              <p>Средняя оценка</p>
              <p>5</p>
            </div>
          </Block>
        </div>
        {location.pathname === '/profile' && (
          <div className={s.blockTasks}>
            <h1 className={style.title}>{selectedTeam}</h1>
            <p className={s.tasks}>Мои задачи</p>
            <TasksUser data={currentExecutorr} currentName={currentName} />
          </div>
        )}
        <Outlet />
      </div>
    </Header>
  );
};
