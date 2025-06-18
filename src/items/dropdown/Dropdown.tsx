import { useEffect, useRef, useState } from 'react';
import { Block } from '../block/Block';
import { Button } from '../button/Button';
import s from './Dropdown.module.scss';
import { DropdownItem } from '../dropdown-item/DropdownItem';

export type ListProps = {
  name: string;
};
type DropdownProps = {
  title: string;
  data: ListProps[];
  selectedTeam?: string;
  setSelectedTeam?: (nameTeam: string) => void;
};
export const Dropdown = ({ title, data, selectedTeam, setSelectedTeam }: DropdownProps) => {
  const [openDropdown, setOpenDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const handleOpenDropdown = () => {
    setOpenDropdown((prev) => !prev);
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
  return (
    <div className={s.dropdown} ref={dropdownRef}>
      <Button type={'dropdown'} onClick={handleOpenDropdown} chevron={openDropdown ? 'up' : 'down'}>
        {title}
      </Button>
      {openDropdown && (
        <Block extraClass={s.block}>
          {data.map((list) => (
            <DropdownItem
              title={list.name}
              selectedTeam={selectedTeam}
              setSelectedTeam={setSelectedTeam}
            />
          ))}
        </Block>
      )}
    </div>
  );
};
