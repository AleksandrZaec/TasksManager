import { Modal } from '@items/modal/Modal';
import { allUsers, TaskType } from '@utils/mockData';
import s from './ModalViewTask.module.scss';
import { EditName } from '@items/editTask/editName/EditName';
import { EditDescription } from '@items/editTask/editDescription/EditDescription';
import { EditPriority } from '@items/editTask/editPriority/EditPriority';
import { EditStatus } from '@items/editTask/editStatus/EditStatus';
import { ExecutorSelect } from '@items/editTask/editExecutor/editExecutor';

type ModalViewTaskProps = {
  isOpen: boolean;
  setOpen: (value: boolean) => void;
  task: TaskType;
};

export const ModalViewTask = ({ isOpen, setOpen, task }: ModalViewTaskProps) => {
  return (
    <Modal isOpen={isOpen} onClose={() => setOpen(false)}>
      <h1>Задача № {task.id}</h1>
      <div className={s.container}>
        <div className={s.task}>
          <EditName task={task} />
          <div className={s.manager}>
            <p>Задачу создал</p>
            <p> {task.manager}</p>
          </div>
          <EditPriority task={task} />
          <EditStatus task={task} />
          <ExecutorSelect task={task} allUsers={allUsers} />
          <EditDescription task={task} />
        </div>
        <div>
          <h1>Комментарии</h1>
        </div>
      </div>
    </Modal>
  );
};
