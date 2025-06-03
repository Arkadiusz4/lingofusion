import React from "react";
import "./Button.css";

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode;
    className?: string;
}

export default function Button({children, className = "", ...props}: Props) {
    return (
        <button
            {...props}
            className={`button ${className} ${props.disabled ? "button--disabled" : ""}`}
        >
            {children}
        </button>
    );
}
