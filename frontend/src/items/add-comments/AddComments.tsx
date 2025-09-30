import s from './AddComments.module.scss';
import { TextArea } from '@items/text-area/TextArea';
import { Button } from '@items/button/Button';
import { useState } from 'react';

type AddCommentProps = {
  userName: string;
  onSave: (text: string) => void;
  onCancelEdit: () => void;
};

export const AddComment = ({ userName, onSave }: AddCommentProps) => {
  const [text, setText] = useState('');
  const handleSave = () => {
    if (text.trim()) {
      onSave(text.trim());
      setText('');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };
  const handleCancelClick = () => {
    setText('');
  };
  return (
    <div className={s.addComment}>
      <p className={s.title}>
        Пользователь: <b>{userName}</b>
      </p>
      <TextArea
        extraClass={s.block}
        value={text}
        onChange={handleChange}
        placeholder='Введите комментарий'
        rows={4}
      />
      <Button type={'outline'} onClick={handleSave}>
        Добавить
      </Button>
      <Button type={'outline'} onClick={handleCancelClick}>
        Отмена
      </Button>
    </div>
  );
};
