import { Modal } from '@items/modal/Modal';
import { allUsers, CommentType, TaskType, UserInfo } from '@utils/mockData';
import s from './ModalViewTask.module.scss';
import { EditName } from '@items/editTask/editName/EditName';
import { EditDescription } from '@items/editTask/editDescription/EditDescription';
import { EditPriority } from '@items/editTask/editPriority/EditPriority';
import { EditStatus } from '@items/editTask/editStatus/EditStatus';
import { EditExecutor } from '@items/editTask/editExecutor/EditExecutor';
import { Comments } from '@items/comments/Comments';
import { useState } from 'react';
import { IconsItem } from '@items/iconsItem/IconsItem';

type ModalViewTaskProps = {
  isOpen: boolean;
  setOpen: (value: boolean) => void;
  task: TaskType;
  currentUser: UserInfo;
};

export const ModalViewTask = ({ isOpen, setOpen, task, currentUser }: ModalViewTaskProps) => {
  const [comments, setComments] = useState<CommentType[]>(task.comment);
  const [editComment, setEditComment] = useState<string | null>(null);

  const handleAddNewComment = (text: string) => {
    const newComment: CommentType = {
      id: Date.now().toString(),
      description: text,
      date: new Date().toISOString(),
      user: currentUser,
    };
    setComments((prev) => [...prev, newComment]);
  };

  const handleSaveComment = (text: string) => {
    if (editComment) {
      setComments((prev) =>
        prev.map((c) => (c.id === editComment ? { ...c, description: text } : c)),
      );
      setEditComment(null);
    } else {
      handleAddNewComment(text);
    }
  };

  const handleEditComment = (id: string, newText: string) => {
    setComments((prev) => prev.map((c) => (c.id === id ? { ...c, description: newText } : c)));
    setEditComment(null);
  };

  const handleDeleteComment = (commentId: string) => {
    setComments((prev) => prev.filter((c) => c.id !== commentId));
  };

  const handleCancelEdit = () => {
    setEditComment(null);
  };
  return (
    <Modal isOpen={isOpen} onClose={() => setOpen(false)}>
      <div className={s.modalTitle}>
        <h1 className={s.titleTask}>Задача № {task.id}</h1>
        <IconsItem src='/icons/close.png' alt='close' onClick={() => setOpen(false)} />
      </div>
      <div className={s.container}>
        <div className={s.task}>
          <EditName task={task} />
          <div className={s.manager}>
            <p>Задачу создал</p>
            <p> {task.manager}</p>
          </div>
          <EditPriority task={task} />
          <EditStatus task={task} />
          <EditExecutor task={task} allUsers={allUsers} />
          <EditDescription task={task} />
        </div>
        <div className={s.commentModal}>
          <h1 className={s.commentTask}>Комментарии</h1>
          <Comments
            comments={comments}
            onEdit={handleEditComment}
            user={currentUser}
            handleSaveComment={handleSaveComment}
            handleAddNewComment={handleAddNewComment}
            handleCancelEdit={handleCancelEdit}
            handleDeleteComment={handleDeleteComment}
            currentUserId={currentUser.uuid}
            lengthAllComments={comments.length}
          />
        </div>
      </div>
    </Modal>
  );
};
