import React from "react";
import "./ResultDisplay.css";

interface Highlight {
    start: number;
    end: number;
    suggestion: string;
}

interface Props {
    output: string;
    highlights?: Highlight[];
    dataPlaceholder?: string;
}

export default function ResultDisplay({
                                          output,
                                          highlights = [],
                                          dataPlaceholder = "",
                                      }: Props) {
    if (highlights.length === 0 && output === "") {
        return (
            <div className="result-card">
                <pre className="result result-placeholder">{dataPlaceholder}</pre>
            </div>
        );
    }

    if (highlights.length === 0) {
        return (
            <div className="result-card">
                <pre className="result">{output}</pre>
            </div>
        );
    }

    let last = 0;
    const parts: React.ReactNode[] = highlights.map((h, i) => {
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
    parts.push(<React.Fragment key="last">{output.slice(last)}</React.Fragment>);

    return (
        <div className="result-card">
            <pre className="result">{parts}</pre>
        </div>
    );
}
