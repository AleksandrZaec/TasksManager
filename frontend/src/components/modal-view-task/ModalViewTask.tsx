import { Modal } from '@items/modal/Modal';
import { TaskType } from '@utils/mockData';
import s from './ModalViewTask.module.scss';
import { EditName } from '@items/editTask/editName/EditName';

type ModalViewTaskProps = {
  isOpen: boolean;
  setOpen: (value: boolean) => void;
  task: TaskType;
};
export const ModalViewTask = ({ isOpen, setOpen, task }: ModalViewTaskProps) => {
  
  const executor = task.executor;

  const executorText = Array.isArray(executor) ? executor.join(', ') : executor;
  return (
    <Modal isOpen={isOpen} onClose={() => setOpen(false)}>
      <h1>Задача № {task.id}</h1>
      <div className={s.container}>
        <div className={s.task}>
          <EditName task={task} />
          <p>Задачу создал {task.manager}</p>
          <p>Приоритет задачи {task.priority}</p>
          <p>Статус задачи {task.status}</p>
          <p>Исполнители {executorText}</p>
          <div>
            <h1>Описание задачи</h1>
            <p>{task.description}</p>
          </div>
        </div>
        <div>
          <h1>Комментарии</h1>
        </div>
      </div>
    </Modal>
  );
};
