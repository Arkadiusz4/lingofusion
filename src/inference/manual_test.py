from pathlib import Path
from src.inference.translate import load_translation_model, translate


def main():
    project_root = Path(__file__).resolve().parents[2]
    adapter_dir = project_root / "checkpoints" / "mt_lora_r8_a16_d0_e5"
    base_model = "gsarti/opus-mt-tc-en-pl"

    model, tokenizer, device = load_translation_model(str(adapter_dir), base_model)

    examples = [
        "Hello, how are you?",
        "The quick brown fox jumps over the lazy dog.",
        "Yesterday I went to the store to buy some fruit.",
        "Natural language processing is fascinating.",
        "I live in Warsaw and I love pierogi.",
        # bardziej złożone:
        "Despite the heavy rain, the parade continued, much to the delight of the spectators.",
        "If I had known about the traffic, I would have left earlier to arrive on time.",
        "Quantum computing promises to solve certain problems exponentially faster than classical computers.",
        # Trudniejsze
        "Notwithstanding the financial downturn, the startup managed to secure funding from multiple angel investors.",
        "Recent advancements in deep reinforcement learning have revolutionized robotics and autonomous systems.",
        "If the temperature drops below freezing, the water in the pipes can crystallize and cause serious damage.",
        "While the committee was deliberating, an unexpected announcement changed the course of the negotiations.",
        "Advances in quantum error correction are vital for the scalable realization of quantum computing architectures.",
        # Zdania złożone i trudniejsze
        "Had she known the consequences of her actions — which, surprisingly, involved both legal and ethical quandaries spanning multiple jurisdictions — she might have sought counsel before proceeding.",
        "He decided to bite the bullet and go all-in on the startup, even though that meant burning the midnight oil for weeks on end.",
        "The contract stipulated that any breach thereof, notwithstanding the occurrence of force majeure events, would entitle the aggrieved party to injunctive relief.",
        "Extracorporeal membrane oxygenation is indicated in patients with refractory hypoxemia despite maximal ventilatory support.",
        "Rarely have I encountered a thesis so meticulously researched and cogently argued, spanning disciplines from epistemology to quantum field theory.",
        "Although the committee — after three days of exhaustive hearings, dozens of expert testimonies, and hours of heated debate — had come to a tentative consensus, further ratification was deferred.",
        "The symposium addressed AI safety, algorithmic bias, data privacy, federated learning, reinforcement learning, transfer learning, and the ethical implications of autonomous systems.",
        "In the event horizon of a Kerr–Newman black hole, frame-dragging effects become so pronounced that test particles follow spiral geodesics.",
        "Under the pallid light of the waning moon, the abandoned cathedral’s shadows seemed to whisper secrets of a bygone era.",
        "Archduke Ferdinand’s assassination in Sarajevo, an event both tragic and inadvertent, precipitated the conflagration of World War I.",
        "The research concluded that, all things considered, the participants’ kinesthetic learning styles flourished, so yeah, they really nailed the whole hands-on approach.",
        "Only 2.5% of the surveyed population, comprising over 10,000 individuals across five continents, reported adverse side effects.",
        "If and only if the matrix is both symmetric and positive definite does the Cholesky decomposition yield a unique lower-triangular factor.",
        "The hedge fund’s portfolio, leveraged at 3:1 and hedged against currency fluctuations, underperformed the benchmark by 0.75 basis points.",
        "Despite the crescendo of debate over GDPR compliance, the start-up pivoted to a freemium SaaS model, touting zero-day patching and SLO-backed SLAs."
    ]

    for src in examples:
        tgt = translate(src, model, tokenizer, device)[0]
        print(f"> {src}\n< {tgt}\n")


if __name__ == "__main__":
    main()
