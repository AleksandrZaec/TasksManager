import clsx from 'clsx';
import s from './Dropdown.module.scss';

type DropdownItemProps = {
  title: string;
  selectedTeam?: string;
  setSelectedTeam?: (nameTeam: string) => void;
};
export const DropdownItem = ({ title, selectedTeam, setSelectedTeam }: DropdownItemProps) => {
  return (
    <p
      onClick={() => setSelectedTeam?.(title)}
      key={title}
      className={clsx(s.title, { [s.selected]: title === selectedTeam })}>
      {title}
    </p>
  );
};
