import { useEffect, useRef, useState } from 'react';
import { Block } from '@items/block/Block';
import { Button } from '@items/button/Button';
import s from './Dropdown.module.scss';
import { DropdownItem } from '@items/dropdown-item/DropdownItem';
import clsx from 'clsx';
import style from '@items/dropdown-item/Dropdown.module.scss';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@route/Routes';

export type ListProps = {
  name: string;
};
type DropdownProps = {
  title: string;
  data?: ListProps[];
  profile?: boolean;
  selectedTeam?: string;
  setSelectedTeam?: (nameTeam: string) => void;
};
export const Dropdown = ({
  title,
  data,
  profile,
  selectedTeam,
  setSelectedTeam,
}: DropdownProps) => {
  const [openDropdown, setOpenDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const handleOpenDropdown = () => {
    setOpenDropdown((prev) => !prev);
  };

  const handleNavigateProfile = () => {
    navigate(ROUTES.PROFILE);
  };

  useEffect(() => {
    const handleClose = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpenDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClose);
    return () => {
      document.removeEventListener('mousedown', handleClose);
    };
  }, []);
  const handleTitle = (title: string) => {
    setSelectedTeam?.(title);
    setOpenDropdown(false);
  };
  return (
    <div className={s.dropdown} ref={dropdownRef}>
      <Button type={'dropdown'} onClick={handleOpenDropdown} chevron={openDropdown ? 'up' : 'down'}>
        {title}
      </Button>
      {openDropdown && (
        <Block extraClass={clsx(s.block, { [s.profile]: profile })}>
          {profile ? (
            <>
              <p className={style.title} onClick={handleNavigateProfile}>
                Профиль
              </p>
              <p className={style.title}>Выйти</p>
            </>
          ) : (
            data?.map((listItem) => (
              <DropdownItem
                key={listItem.name}
                title={listItem.name}
                selectedTeam={selectedTeam}
                onSelect={handleTitle}
              />
            ))
          )}
        </Block>
      )}
    </div>
  );
};
