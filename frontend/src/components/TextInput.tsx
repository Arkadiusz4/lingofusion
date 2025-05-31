import "./TextInput.css";

interface Props {
    value: string;
    onChange: (v: string) => void;
    placeholder?: string;
    id?: string;
}

export default function TextInput({value, onChange, placeholder, id}: Props) {
    return (
        <textarea
            id={id}
            className="text-input"
            rows={6}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            aria-label="Pole tekstowe"
        />
    );
}
