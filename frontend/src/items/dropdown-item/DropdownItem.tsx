import clsx from 'clsx';
import s from './Dropdown.module.scss';

type DropdownItemProps = {
  title: string;
  selectedTeam?: string;
  onSelect?: (nameTeam: string) => void;
  isActive?: boolean;
};
export const DropdownItem = ({ title, selectedTeam, onSelect, isActive }: DropdownItemProps) => {
  const handleTitle = () => {
    onSelect?.(title);
  };
  return (
    <p
      onClick={handleTitle}
      key={title}
      className={clsx(s.title, { [s.selected]: title === selectedTeam }, { [s.active]: isActive })}>
      {title}
    </p>
  );
};
