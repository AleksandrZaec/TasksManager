import { Button } from '@items/button/Button';
import { TextArea } from '@items/text-area/TextArea';
import { useState } from 'react';
import s from './EditName.module.scss';
import { TaskType } from '@utils/mockData';
import { IconsItem } from '@items/iconsItem/IconsItem';

type EditNameProps = {
  task: TaskType;
};
export const EditName = ({ task }: EditNameProps) => {
  const [editedTask, setEditedTask] = useState(task);
  const [isEditingName, setIsEditingName] = useState(false);
  const handleEditName = () => {
    setIsEditingName(true);
  };
  const handleCancel = () => {
    setIsEditingName(false);
  };
  return (
    <div className={s.name}>
      {isEditingName ? (
        <div className={s.container}>
          <TextArea
            value={editedTask.name}
            onChange={(e) => setEditedTask({ ...editedTask, name: e.target.value })}
            autoFocus
            extraClass={s.textarea}
          />
          <div className={s.buttonGroup}>
            <Button type={'text'}>Сохранить</Button>
            <Button type={'text'} onClick={handleCancel}>
              Отменить
            </Button>
          </div>
        </div>
      ) : (
        <>
          <h1>{task.name}</h1>
          <IconsItem src='/icons/reName.png' alt='reName' onClick={handleEditName} />
        </>
      )}
    </div>
  );
};
