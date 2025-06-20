import { useState } from 'react';
import { Button } from '../../items/button/Button';
import { TaskList } from '../../items/task-list/TaskList';
import { Header } from '../header/Header';
import s from './Main.module.scss';
import { mockData, TaskType } from '../../mockData';

export const Main = () => {
  const [selectedTeam, setSelectedTeam] = useState<string>('Team1');
  const statusTask = mockData.reduce<Record<string, TaskType[]>>((acc, task) => {
    acc[task.status] = acc[task.status] ? [...acc[task.status], task] : [task];
    return acc;
  }, {});
  return (
    <Header setSelectedTeam={setSelectedTeam} selectedTeam={selectedTeam}>
      <div className={s.content}>
        <div className={s.main}>
          <div className={s.blockWithIcon}>
            <h1 className={s.title}>{selectedTeam}</h1>
            <img src='/icons/reName.png' alt='rename' className={s.icon} />
          </div>
          <div className={s.blockWithButton}>
            <p className={s.subTitle}>Участников: 10</p>
            <Button type={'outline'} extraClass={s.button} icon={true}>
              Добавить участников
            </Button>
          </div>
        </div>
        <div className={s.main}>
          <p className={s.subTitle}>Список задач</p>
        </div>
        <TaskList data={statusTask} />
      </div>
    </Header>
  );
};
