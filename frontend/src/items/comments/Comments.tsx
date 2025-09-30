import s from './comments.module.scss';
import { AddComment } from '@items/add-comments/AddComments';
import { CommentType, UserInfo } from '@utils/mockData';
import { Comment } from '@items/comment/Comment';
import { Scroll } from '@items/scroll/Scroll';

type CommentsProps = {
  comments: CommentType[];
  user: UserInfo;
  handleSaveComment: (commentText: string) => void;
  handleAddNewComment: (commentText: string) => void;
  handleCancelEdit: () => void;
  handleDeleteComment: (commentId: string) => void;
  currentUserId: number;
  lengthAllComments: number;
  onEdit: (id: string, newText: string) => void;
};

export const Comments = ({
  comments,
  user,
  handleSaveComment,
  handleCancelEdit,
  handleDeleteComment,
  lengthAllComments,
  onEdit,
}: CommentsProps) => {
  return (
    <>
      <AddComment userName={user.name} onSave={handleSaveComment} onCancelEdit={handleCancelEdit} />
      <Scroll extraClass={s.scroll}>
        {comments.length === 0 ? (
          <p>Комментариев пока нет</p>
        ) : (
          comments.map(({ id, description, date, user: commentUser }) => (
            <Comment
              key={id}
              comment={{ id, description, date, user: commentUser }}
              onEdit={(newText) => onEdit(id, newText)}
              onDelete={() => handleDeleteComment(id)}
            />
          ))
        )}
      </Scroll>
      <p className={s.totalComments}>Всего {lengthAllComments}</p>
    </>
  );
};
