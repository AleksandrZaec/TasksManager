import { Block } from '../../items/block/Block';
import { Button } from '../../items/button/Button';
import { Dropdown } from '../../items/dropdown/Dropdown';
import { listTeams, profileList } from '../../mockData';
import s from './Header.module.scss';

type HeaderProps = {
  children: React.ReactNode;
  selectedTeam: string;
  setSelectedTeam: (nameTeam: string) => void;
};
export const Header = ({ children, setSelectedTeam, selectedTeam }: HeaderProps) => {
  return (
    <div className={s.container}>
      <div className={s.menu}>
        <Block extraClass={s.header}>
          <Button type={'outline'} icon={true} extraClass={s.button}>
            Добавить команду
          </Button>
          <Dropdown
            title={'Список команд'}
            data={listTeams}
            selectedTeam={selectedTeam}
            setSelectedTeam={setSelectedTeam}></Dropdown>
          <Button type={'dropdown'}>Календарь</Button>
          <Button type={'dropdown'}>Встречи</Button>
          <Dropdown title={'Профиль'} list={profileList}></Dropdown>
        </Block>
        {children}
      </div>
    </div>
  );
};
