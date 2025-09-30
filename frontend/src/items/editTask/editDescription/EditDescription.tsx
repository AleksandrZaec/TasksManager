import { Button } from '@items/button/Button';
import { TextArea } from '@items/text-area/TextArea';
import { useState } from 'react';
import s from './EditDescription.module.scss';
import { TaskType } from '@utils/mockData';
import { IconsItem } from '@items/iconsItem/IconsItem';

type EditDescriptionProps = {
  task: TaskType;
};
export const EditDescription = ({ task }: EditDescriptionProps) => {
  const [editedTask, setEditedTask] = useState(task);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const handleEditDescription = () => {
    setIsEditingDescription(true);
  };
  const handleCancel = () => {
    setIsEditingDescription(false);
  };
  return (
    <div className={s.description}>
      {isEditingDescription ? (
        <div className={s.container}>
          <TextArea
            value={editedTask.description}
            onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })}
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
          <h1>{task.description}</h1>
          <IconsItem src='/icons/reName.png' alt='reName' onClick={handleEditDescription} />
        </>
      )}
    </div>
  );
};
