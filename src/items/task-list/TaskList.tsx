import { TaskType } from '../../components/main/mockData';
import { Block } from '../block/Block';
import { Button } from '../button/Button';
import { Scroll } from '../scroll/Scroll';
import { Task } from '../task/Task';
import s from './TaskList.module.scss';

type TaskTableProps = {
  data: Record<string, TaskType[]>;
};
export const TaskList = ({ data }: TaskTableProps) => {
  const statuss = [
    { status: 'Ожидает', icon: '/icons/pending.svg', className: 'pending' },
    { status: 'В процессе', icon: '/icons/in-progress.svg', className: 'inProgress' },
    { status: 'Готово', icon: '/icons/done.svg', className: 'done' },
  ];
  const column = [
    'Имя задачи',
    'Номер задачи',
    'Срок сдачи',
    'Ответственный',
    'Задачу создал',
    'Приоритет',
  ];
  return (
    <div className={s.tasks}>
      {statuss.map((statusList) => (
        <Block key={statusList.status}>
          <div className={s.list}>
            <div className={`${s.statusIcons} ${s[statusList.className]}`}>
              <img src={statusList.icon} alt='icons' className={s.icon} />
              <p>{statusList.status}</p>
            </div>
            <div className={s.title}>
              {column.map((columnList) => (
                <p>{columnList}</p>
              ))}
            </div>
            <Scroll extraClass={s.scroll}>
              {data[statusList.status].map((task) => (
                <div key={task.id}>
                  <Task task={task} />
                </div>
              ))}
            </Scroll>
          </div>
          <Button type={'text'} icon={true} extraClass={s.button}>Добавить задачу</Button>
        </Block>
      ))}
    </div>
  );
};
