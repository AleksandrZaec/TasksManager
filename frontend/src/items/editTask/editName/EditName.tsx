import { Button } from '@items/button/Button';
import { TextArea } from '@items/text-area/TextArea';
import { useState } from 'react';
import style from '@components/main/Main.module.scss';
import s from './EditName.module.scss';
import { TaskType } from '@utils/mockData';

type EditNameProps = {
  task: TaskType;
};
export const EditName = ({ task }: EditNameProps) => {
  const [editedTask, setEditedTask] = useState(task);
  const [isEditingName, setIsEditingName] = useState(false);
  const handleEditName = () => {
    setIsEditingName(true);
  };
  return (
    <div className={s.name}>
      {isEditingName ? (
        <>
          <TextArea
            value={editedTask.name}
            onChange={(e) => setEditedTask({ ...editedTask, name: e.target.value })}
            onBlur={() => setIsEditingName(false)}
            autoFocus
            extraName={s.textarea}
          />
          <Button type={'text'}>Сохранить</Button>
        </>
      ) : (
        <>
          <h1>{task.name}</h1>
          <img
            src='/icons/reName.png'
            alt='rename'
            className={style.icon}
            onClick={handleEditName}
          />
        </>
      )}
    </div>
  );
};
