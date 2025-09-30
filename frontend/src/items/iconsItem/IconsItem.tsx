import s from './IconsItem.module.scss';

type IconsItemProps = {
  onClick: () => void;
  src: string;
  alt: string;
};
export const IconsItem = ({ onClick, src, alt }: IconsItemProps) => {
  return <img src={src} alt={alt} className={s.icon} onClick={onClick} />;
};
