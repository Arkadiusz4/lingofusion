import './ModeToggle.css';

interface Props {
    mode: 'translate' | 'gec';
    onChange: (m: 'translate' | 'gec') => void;
}

// Drobne ulepszenie: zachowujemy klasę z zewnątrz, jeśli trzeba dać margin
export default function ModeToggle({mode, onChange}: Props) {
    return (
        <div className="mode-toggle">
            <button
                className={mode === 'translate' ? 'active' : ''}
                onClick={() => onChange('translate')}
                aria-label="Tryb tłumaczenia"
            >
                Tłumacz
            </button>
            <button
                className={mode === 'gec' ? 'active' : ''}
                onClick={() => onChange('gec')}
                aria-label="Tryb korekty"
            >
                Korekta
            </button>
        </div>
    );
}
