import React from 'react';
import '../styles/ResultDisplay.css';

interface Highlight {
    start: number;
    end: number;
    suggestion: string;
}

interface Props {
    output: string;
    highlights?: Highlight[];
}

export default function ResultDisplay({output, highlights, dataPlaceholder}: Props & { dataPlaceholder?: string }) {
    if (!highlights?.length && !output) {
        return <pre className="result" data-placeholder={dataPlaceholder || ''}/>;
    }

    let last = 0;
    const parts = highlights.map((h, i) => {
        const before = output.slice(last, h.start);
        const wrong = output.slice(h.start, h.end);
        last = h.end;
        return (
            <React.Fragment key={i}>
                {before}
                <span className="highlight" title={h.suggestion}>
          {wrong}
        </span>
            </React.Fragment>
        );
    });
    parts.push(output.slice(last));
    return <pre className="result">{parts}</pre>;
}
