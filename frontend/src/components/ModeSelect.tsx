interface Props {
    value: string;
    onChange: (v: any) => void;
}

export default function ModeSelect({value, onChange}: Props) {
    return (
        <select value={value} onChange={e => onChange(e.target.value)}>
            <option value="translate-pl-en">PL → EN</option>
            <option value="translate-en-pl">EN → PL</option>
            <option value="gec-en">Korekta EN</option>
        </select>
    );
}
