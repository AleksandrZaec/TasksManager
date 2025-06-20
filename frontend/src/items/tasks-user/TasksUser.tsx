import { useMemo, useState } from 'react';
import { columnUser, TaskType, titles } from '@utils/mockData';
import { Block } from '@items/block/Block';
import { Scroll } from '@items/scroll/Scroll';
import { Task } from '@items/task/Task';
import s from './TasksUser.module.scss';
import clsx from 'clsx';

type TaskTableProps = {
  data: TaskType[];
  currentName?: string;
};
export const TasksUser = ({ data, currentName }: TaskTableProps) => {
  const [activeStatus, setActiveStatus] = useState<string>('Все');
  const statusTask = useMemo(() => {
    return data.reduce<Record<string, TaskType[]>>((acc, task) => {
      acc[task.status] = acc[task.status] ? [...acc[task.status], task] : [task];
      return acc;
    }, {});
  }, [data]);
  const tasksUser = activeStatus === 'Все' ? data : statusTask[activeStatus] || [];
  return (
    <div>
      <div className={s.allTitle}>
        {titles.map((title) => (
          <p
            key={title}
            className={`${s.title} ${activeStatus === title ? s.active : ''}`}
            onClick={() => setActiveStatus(title)}>
            {title}
          </p>
        ))}
      </div>

      <Block extraClass={clsx(s.block, { [s.blockTasks]: activeStatus === 'Все' })}>
        <div className={s.list}>
          <div className={`${s.statusIcons} `}></div>
          {tasksUser.length > 0 ? (
            <div className={s.subTitle}>
              {columnUser.map((columnList, index) => (
                <p key={index}>{columnList}</p>
              ))}
            </div>
          ) : null}

          <Scroll extraClass={s.scroll}>
            {tasksUser.length > 0 ? (
              tasksUser.map((task) => (
                <div key={task.id}>
                  <Task task={task} currentName={currentName} />
                </div>
              ))
            ) : (
              <p>Задачи отсутствуют</p>
            )}
          </Scroll>
        </div>
      </Block>
    </div>
  );
};
