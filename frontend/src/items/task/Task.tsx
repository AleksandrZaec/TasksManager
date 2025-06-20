import clsx from 'clsx';
import { TaskType } from '../../mockData';
import s from './Task.module.scss';

type TaskProps = {
  task: TaskType;
  currentName?: string;
};

export const Task = ({ task, currentName }: TaskProps) => {
  return (
    <div className={clsx(s.task, { [s.currentName]: currentName })}>
      <p>{task.name}</p>
      {!currentName && <p>{task.id}</p>}
      <p>{task.date}</p>
      <p>{task.executor}</p>
      {!currentName && <p>{task.manager}</p>}
      <p>{task.priority}</p>
    </div>
  );
};
