import { useState } from 'react';
import { Header } from '../header/Header';
import s from './Profile.module.scss';
import style from '../main/Main.module.scss';
import { Block } from '../../items/block/Block';
import { Button } from '../../items/button/Button';
import { mockData } from '../../mockData';
import { TasksUser } from '../../items/tasks-user/TasksUser';
import { Outlet, useNavigate } from 'react-router-dom';
import { ROUTES } from '../../route/Routes';

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
      <div className={s.container}>
        <div className={s.blockData}>
          <Block extraClass={s.blockUser}>
            <h1 className={s.title}>{'Иванов Иван'}</h1>
            <p>ID</p>
            {selectedTeam && <p>Роль в {selectedTeam}</p>}
            <p>Почта</p>
            <Button type={'outline'} onClick={handleSetting}>
              Редактировать
            </Button>
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
            <p>Мои задачи</p>
            <TasksUser data={currentExecutorr} currentName={currentName} />
          </div>
        )}
        <Outlet/>
      </div>
    </Header>
  );
};
