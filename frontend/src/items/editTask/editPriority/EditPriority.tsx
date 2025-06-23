import { priority, TaskType } from '@utils/mockData';
import s from './EditPriority.module.scss';
import { Dropdown } from '@items/dropdown/Dropdown';
import { useState } from 'react';

type EditPriorityProps = {
  task: TaskType;
};
export const EditPriority = ({ task }: EditPriorityProps) => {
  const [selectedPriority, setSelectedPriority] = useState(task.priority ?? 'Низкий');

  return (
    <div className={s.container}>
      <p>Приоритет задачи</p>
      <Dropdown
        title={'Низкий'}
        data={priority.map((p) => ({ name: p }))}
        defaultValue={selectedPriority}
        onSelectValue={setSelectedPriority}
      />
    </div>
  );
};
