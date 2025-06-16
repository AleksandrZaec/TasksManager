import React from "react"
import s from './Button.module.scss';

type ButtonProps = {
    children: React.ReactNode
}
export const Button = ({children}: ButtonProps) => {
  return (
    <button className={s.button}>
      {children}
    </button>
  )
}

