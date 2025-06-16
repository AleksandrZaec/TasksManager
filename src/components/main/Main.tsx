import { Button } from '../../items/button/Button';
import { TaskList } from '../../items/task-list/TaskList';
import { Header } from '../header/Header';
import s from './Main.module.scss';
import { mockData, TaskType } from './mockData';

export const Main = () => {
  const statusTask = mockData.reduce<Record<string, TaskType[]>>((acc, task) => {
    acc[task.status] = acc[task.status] ? [...acc[task.status], task] : [task];
    return acc;
  }, {});
  return (
    <Header>
      <div className={s.content}>
        <div className={s.main}>
          <h1>Название команды</h1>
          <p>Участников: 10</p>
          <Button type={'outline'} extraClass={s.button} icon={true}>
            Добавить участников
          </Button>
        </div>
        <div className={s.main}>
          <p>Список задач</p>
        </div>
        <div>
          <TaskList data={statusTask} />
        </div>
      </div>
    </Header>
  );
};
