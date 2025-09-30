import { useState, useCallback, useEffect, useRef } from 'react';
import s from './Comment.module.scss';
import { Button } from '@items/button/Button';
import { TextArea } from '@items/text-area/TextArea';
import { formatDate } from '@utils/mockData';

export type CommentType = {
  id: string;
  description: string;
  date: string;
  user: {
    name: string;
  };
};

export type CommentProps = {
  comment: CommentType;
  onEdit: (id: string, newText: string) => void;
  onDelete: (id: string) => void;
};

export const Comment = ({ comment, onEdit, onDelete }: CommentProps) => {
  const { id, description, date, user } = comment;

  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(description);

  const commentRef = useRef<HTMLDivElement>(null);

  const handleClickOutside = useCallback(
    (event: MouseEvent) => {
      if (commentRef.current && !commentRef.current.contains(event.target as Node)) {
        setIsEditing(false);
        setEditText(description);
      }
    },
    [description],
  );

  useEffect(() => {
    if (isEditing) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isEditing, handleClickOutside]);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleDeleteClick = () => {
    onDelete(id);
  };

  const handleSaveClick = () => {
    onEdit(editText.trim(), id);
    setIsEditing(false);
  };

  const handleCancelClick = () => {
    setIsEditing(false);
    setEditText(description);
  };

  return (
    <div className={s.comment} ref={commentRef}>
      <h3 className={s.author}>{user.name}</h3>
      {isEditing ? (
        <TextArea
          extraClass={s.block}
          value={editText}
          onChange={(e) => setEditText(e.target.value)}
          rows={3}
        />
      ) : (
        <p className={s.description}>{description}</p>
      )}
      <p className={s.date}>{formatDate(date)}</p>
      <div className={s.buttons}>
        {isEditing ? (
          <>
            <Button type={'text'} onClick={handleSaveClick}>
              Сохранить
            </Button>
            <Button type={'text'} onClick={handleCancelClick}>
              Отмена
            </Button>
          </>
        ) : (
          <>
            <Button type={'text'} onClick={handleEditClick}>
              Редактировать
            </Button>
            <Button type={'text'} onClick={handleDeleteClick}>
              Удалить
            </Button>
          </>
        )}
      </div>
    </div>
  );
};
