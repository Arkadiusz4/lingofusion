from omegaconf import DictConfig, OmegaConf
import hydra


@hydra.main(version_base="1.2", config_path="../../config", config_name="default")
def get_cfg(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))


if __name__ == "__main__":
    get_cfg()
