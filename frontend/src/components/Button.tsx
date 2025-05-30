import React from 'react';
import '../styles/Button.css';

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode;
}

export default function Button({children, ...props}: Props) {
    return (
        <button
            {...props}
            className={`button ${props.disabled ? 'button--disabled' : ''}`}
        >
            {children}
        </button>
    );
}
