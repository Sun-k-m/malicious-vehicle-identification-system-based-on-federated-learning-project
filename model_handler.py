import joblib
from pathlib import Path

class ModelHandler:
    @staticmethod
    def load_model(base_path: Path):
        """
            加载预训练模型和模型元数据。

            base_path: 应用程序的基础路径。
            返回: 加载的模型对象和模型元数据字典。
        """
        model_path = base_path / "saved_models" / "global_model.pkl"
        metadata_path = base_path / "saved_models" / "model_metadata.pkl"
        try:
            model = joblib.load(model_path)
            metadata = joblib.load(metadata_path)
            return model, metadata
        except FileNotFoundError as e:
            raise FileNotFoundError(f"模型或元数据文件未找到: {e}. 请确保 'saved_models' 文件夹存在且包含 'global_model.pkl' 和 'model_metadata.pkl'")
        except Exception as e:
            raise Exception(f"加载模型时发生错误: {e}")