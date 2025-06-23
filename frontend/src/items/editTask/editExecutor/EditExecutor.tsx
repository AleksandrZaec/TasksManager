import { useState } from 'react';
import s from './EditExecutor.module.scss';
import style from '@items/dropdown/Dropdown.module.scss';
import { TaskType } from '@utils/mockData';
import { Block } from '@items/block/Block';
import { DropdownItem } from '@items/dropdown-item/DropdownItem';
import { Button } from '@items/button/Button';
import clsx from 'clsx';

type User = {
  id: number;
  name: string;
};

type ExecutorSelectProps = {
  allUsers: User[];
  task: TaskType;
};

export const ExecutorSelect = ({ allUsers, task }: ExecutorSelectProps) => {
  const [executors, setExecutors] = useState<User[]>(
    allUsers.filter((u) => task.executor.includes(u.name)),
  );

  const [showList, setShowList] = useState(false);
  const toggleUser = (user: User) => {
    setExecutors((prev) => {
      const exists = prev.find((u) => u.id === user.id);

      if (exists && prev.length === 1) {
        return prev;
      }

      return exists ? prev.filter((u) => u.id !== user.id) : [...prev, user];
    });
  };

  const executorText = executors.map((u) => u.name).join(', ');
  const isSelected = (user: User) => executors.some((u) => u.id === user.id);
  return (
    <div className={s.container}>
      <div className={s.header}>
        <div className={s.executor}>
          <span>Исполнители:</span>
          <p>{executorText}</p>
        </div>

        <Button type={'text'} onClick={() => setShowList((prev) => !prev)} extraClass={s.button}>
          {showList ? 'Скрыть' : 'Выбрать'}
        </Button>
      </div>
      {showList && (
        <Block extraClass={clsx(style.block, s.drop)}>
          {allUsers.map((user) => (
            <DropdownItem
              title={user.name}
              key={user.id}
              onSelect={() => toggleUser(user)}
              isActive={isSelected(user)}
            />
          ))}
        </Block>
      )}
    </div>
  );
};
