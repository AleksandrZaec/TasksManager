import { TaskType } from '../../mockData';
import s from './Task.module.scss';

type TaskProps = {
  task: TaskType;
};

export const Task = ({ task }: TaskProps) => {
  return (
    <div className={s.task}>
      <p>{task.name}</p>
      <p>{task.id}</p>
      <p>{task.date}</p>
      <p>{task.executor}</p>
      <p>{task.manager}</p>
      <p>{task.priority}</p>
    </div>
  );
};
