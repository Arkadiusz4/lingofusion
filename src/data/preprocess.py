import json
from pathlib import Path
from omegaconf import DictConfig
import hydra


def preprocess_mt(cfg: DictConfig):
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / cfg.data.raw
    proc_dir = project_root / cfg.data.processed

    print(f"[PREPROCESS] mode={cfg.mode}, raw={raw_dir}, processed={proc_dir}")
    proc_dir.mkdir(parents=True, exist_ok=True)

    inp = raw_dir / "opensubs.tsv"
    out = proc_dir / "mt_train.jsonl"
    with inp.open(encoding="utf-8") as fin, out.open("w", encoding="utf-8") as fout:
        for line in fin:
            src, tgt = line.strip().split("\t")
            json.dump({"src": src, "tgt": tgt}, fout, ensure_ascii=False)
            fout.write("\n")


@hydra.main(version_base="1.2", config_path="../../config", config_name="default")
def main(cfg: DictConfig):
    if cfg.mode == "translation":
        preprocess_mt(cfg)
    else:
        raise NotImplementedError(f"Mode {cfg.mode} not supported")


if __name__ == "__main__":
    main()
