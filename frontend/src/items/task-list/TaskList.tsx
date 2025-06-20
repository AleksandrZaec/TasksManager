import { allStatus, column, TaskType } from '../../mockData';
import { Block } from '../block/Block';
import { Button } from '../button/Button';
import { Scroll } from '../scroll/Scroll';
import { Task } from '../task/Task';
import s from './TaskList.module.scss';

type TaskTableProps = {
  data: Record<string, TaskType[]>;
};
export const TaskList = ({ data }: TaskTableProps) => {
  return (
    <div className={s.tasks}>
      {allStatus.map((statusList) => (
        <Block key={statusList.status}>
          <div className={s.list}>
            <div className={`${s.statusIcons} ${s[statusList.className]}`}>
              <img src={statusList.icon} alt='icons' className={s.icon} />
              <p>{statusList.status}</p>
            </div>
            <div className={s.title}>
              {column.map((columnList, index) => (
                <p key={index}>{columnList}</p>
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
          {statusList.status === 'Ожидает' && (
            <Button type={'text'} icon={true} extraClass={s.button}>
              Добавить задачу
            </Button>
          )}
        </Block>
      ))}
    </div>
  );
};
