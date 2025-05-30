import '../styles/ModeToggle.css';

interface Props {
    mode: 'translate' | 'gec';
    onChange: (m: 'translate' | 'gec') => void;
}

export default function ModeToggle({mode, onChange}: Props) {
    return (
        <div className="mode-toggle">
            <button
                className={mode === 'translate' ? 'active' : ''}
                onClick={() => onChange('translate')}
            >
                Tłumacz
            </button>
            <button
                className={mode === 'gec' ? 'active' : ''}
                onClick={() => onChange('gec')}
            >
                Korekta
            </button>
        </div>
    );
}
