import { allStatus, column, TaskType } from '@utils/mockData';
import { Block } from '@items/block/Block';
import { Button } from '@items/button/Button';
import { Scroll } from '@items/scroll/Scroll';
import { Task } from '@items/task/Task';
import s from './TaskList.module.scss';
import { useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { ModalViewTask } from '@components/modal-view-task/ModalViewTask';
import { ROUTES } from '@route/Routes';

type TaskTableProps = {
  data: Record<string, TaskType[]>;
};
export const TaskList = ({ data }: TaskTableProps) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<TaskType | null>(null);

  const handleViewTask = (task: TaskType) => {
    setModalOpen(true);
    navigate(`/task/${task.id}`);
  };
  useEffect(() => {
    if (id) {
      const tasks = Object.values(data)
        .flat()
        .find((task) => String(task.id) === id);
      if (tasks) {
        setSelectedTask(tasks);
        setModalOpen(true);
      } else {
        setSelectedTask(null);
        setModalOpen(false);
      }
    }
  }, [id, data]);
  const handleCloseModal = () => {
    setSelectedTask(null);
    setModalOpen(false);
    navigate(ROUTES.HOME);
  };
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
                <div key={task.id} onClick={() => handleViewTask(task)}>
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
      {selectedTask && (
        <ModalViewTask task={selectedTask} isOpen={isModalOpen} setOpen={handleCloseModal} />
      )}
    </div>
  );
};
