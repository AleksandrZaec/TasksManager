import { useState } from 'react';
import { Header } from '../header/Header';
import s from './Profile.module.scss';
import { Block } from '../../items/block/Block';
import { Button } from '../../items/button/Button';
import { mockData } from '../../mockData';
import { TasksUser } from '../../items/tasks-user/TasksUser';

export const Profile = () => {
  const [selectedTeam, setSelectedTeam] = useState<string>('Team1');
  const currentName = 'Иванов';
  const currentExecutorr = mockData.filter((item) => item.executor === currentName);
  return (
    <Header setSelectedTeam={setSelectedTeam} selectedTeam={selectedTeam}>
      <h1 className={s.title}>{selectedTeam}</h1>
      <div className={s.container}>
        <Block extraClass={s.blockData}>
          <h1 className={s.title}>{'Иванов Иван'}</h1>
          <p>ID</p>
          <p>Средная оценка</p>
          {selectedTeam && <p>Роль в {selectedTeam}</p>}
          <p>Почта</p>
          <Button type={'outline'}>Редактировать</Button>
        </Block>
        <div className={s.blockTasks}>
          <p>Мои задачи</p>
          {}
          <TasksUser data={currentExecutorr} currentName={currentName}/>
        </div>
      </div>
    </Header>
  );
};
