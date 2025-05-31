import React from "react";

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
        return <pre className="result" data-placeholder={dataPlaceholder}/>;
    }

    if (highlights.length === 0) {
        return <pre className="result">{output}</pre>;
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

    parts.push(
        <React.Fragment key="last">
            {output.slice(last)}
        </React.Fragment>
    );

    return <pre className="result">{parts}</pre>;
}
