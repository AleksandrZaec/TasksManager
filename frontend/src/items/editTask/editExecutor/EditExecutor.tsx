import { useState } from 'react';
import s from './EditExecutor.module.scss';
import style from '@items/dropdown/Dropdown.module.scss';
import { TaskType, UserInfo } from '@utils/mockData';
import { Block } from '@items/block/Block';
import { DropdownItem } from '@items/dropdown-item/DropdownItem';
import clsx from 'clsx';
import { IconsItem } from '@items/iconsItem/IconsItem';

type EditExecutorProps = {
  allUsers: UserInfo[];
  task: TaskType;
};

export const EditExecutor = ({ allUsers, task }: EditExecutorProps) => {
  const [executors, setExecutors] = useState<UserInfo[]>(
    allUsers.filter((u) => task.executor.some((ex) => ex.uuid === u.uuid)),
  );
  const [showList, setShowList] = useState(false);

  const toggleUser = (user: UserInfo) => {
    setExecutors((prev) => {
      const exists = prev.find((u) => u.uuid === user.uuid);

      if (exists && prev.length === 1) {
        return prev;
      }
      setShowList(false)

      return exists ? prev.filter((u) => u.uuid !== user.uuid) : [...prev, user];
    });
  };

  const executorText = executors.map((u) => u.name).join(', ');
  const isSelected = (user: UserInfo) => executors.some((u) => u.uuid === user.uuid);

  return (
    <div className={s.container}>
      <div className={s.header}>
        <div className={s.executor}>
          <span>Исполнители:</span>
          <p>{executorText}</p>
        </div>
        <div className={s.dropdown}>
          <IconsItem
            src='/icons/plus.png'
            alt='plus'
            onClick={() => setShowList((prev) => !prev)}
          />
          {showList && (
            <Block extraClass={clsx(style.block, s.drop)}>
              {allUsers.map((user) => (
                <DropdownItem
                  title={user.name}
                  key={user.uuid}
                  onSelect={() => toggleUser(user)}
                  isActive={isSelected(user)}
                />
              ))}
            </Block>
          )}
        </div>
      </div>
    </div>
  );
};
