import '../styles/TextInput.css'

interface Props {
    value: string;
    onChange: (v: string) => void;
    placeholder?: string;
}

export default function TextInput({value, onChange, placeholder}: Props) {
    return (
        <textarea
            className="text-input"
            rows={6}
            value={value}
            onChange={e => onChange(e.target.value)}
            placeholder={placeholder}
        />
    );
}
