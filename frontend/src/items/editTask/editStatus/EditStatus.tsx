import { status, TaskType } from '@utils/mockData';
import s from './EditStatus.module.scss';
import { Dropdown } from '@items/dropdown/Dropdown';
import { useState } from 'react';

type EditStatusProps = {
  task: TaskType;
};
export const EditStatus = ({ task }: EditStatusProps) => {
  const [selectedStatus, setSelectedStatus] = useState(task.status ?? 'Ожидает');

  return (
    <div className={s.container}>
      <p>Статус задачи</p>
      <Dropdown
        title={'Низкий'}
        data={status.map((p) => ({ name: p }))}
        defaultValue={selectedStatus}
        onSelectValue={setSelectedStatus}
      />
    </div>
  );
};
