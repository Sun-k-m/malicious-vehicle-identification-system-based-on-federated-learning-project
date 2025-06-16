import pandas as pd
from typing import Dict, List
from tkinter import messagebox
from collections import defaultdict

class DataProcessor:
    def __init__(self, model, metadata):
        self.model = model
        self.metadata = metadata

    def preprocess_input(self, input_data: Dict) -> pd.DataFrame:
        exclude_fields = {'type', 'rcvTime', 'sendTime', 'sender', 'senderPseudo',
                          'messageID', 'vehicleId', 'exchangedMessageType', 'EventID',
                          'EventType', 'RoadID', 'hazardOccurrence', 'savedTimestamp'}

        # 过滤输入数据，排除不必要的字段
        filtered_data = {k: v for k, v in input_data.items() if k not in exclude_fields}
        # 定义一个字典来存储最终处理后的特征
        processed_features = {}

        # 遍历模型期望的所有特征列，按顺序填充 processed_features
        # 确保优先使用 filtered_data 中的值
        for feature_name in self.metadata["feature_columns"]:
            # 检查是否是需要展开的列表字段 (如 pos_0, spd_1, etc.)
            is_vector_feature = False
            for prefix in ['pos_', 'spd_', 'acl_', 'hed_', 'pos_noise_', 'spd_noise_', 'acl_noise_', 'hed_noise_',
                           'sender_GPS_', 'currentDirection_']:
                if feature_name.startswith(prefix):
                    base_name = prefix.rstrip('_')  # 例如 'pos'
                    index_str = feature_name[len(prefix):]  # 例如 '0'
                    if index_str.isdigit():
                        index = int(index_str)
                        is_vector_feature = True
                        if base_name in filtered_data and isinstance(filtered_data[base_name], list) and index < len(
                                filtered_data[base_name]):
                            try:
                                processed_features[feature_name] = float(filtered_data[base_name][index])
                            except (ValueError, TypeError):
                                processed_features[feature_name] = 0.0  # 转换失败用默认值
                        else:
                            processed_features[feature_name] = 0.0  # 基础字段不存在或索引超出范围
                        break

            if not is_vector_feature:  # 如果不是向量展开的字段
                if feature_name in filtered_data:
                    # 对于非列表字段，直接使用 filtered_data 中的值
                    try:
                        processed_features[feature_name] = float(filtered_data[feature_name])
                    except (ValueError, TypeError):
                        # 如果转换失败，或者不是数字类型，使用默认值
                        processed_features[feature_name] = 0.0
                else:
                    # 如果 filtered_data 中没有这个字段，使用默认值 0.0
                    processed_features[feature_name] = 0.0

        # 将处理后的特征转换为 DataFrame
        # 确保DataFrame的列顺序与模型训练时的特征列顺序一致
        df = pd.DataFrame([processed_features], columns=self.metadata["feature_columns"])

        # 确保DataFrame的列与模型的特征列完全一致，并且顺序正确
        df = df.reindex(columns=self.metadata["feature_columns"], fill_value=0.0)

        return df

    def analyze_file_data(self, records: List[Dict], progress_callback=None):
        results = []
        vehicle_attack_counts = defaultdict(int)
        for idx, record in enumerate(records, 1):
            try:
                processed_data = self.preprocess_input(record)
                prediction = self.model.predict(processed_data.values)
                proba = self.model.predict_proba(processed_data.values)

                results.append({
                    "prediction": int(prediction[0]),
                    "attack_prob": float(proba[0][1]),
                    "is_attack": bool(prediction[0])
                })

                if prediction[0] == 1:
                    vehicle_id = record.get("vehicleId", "未知车辆")
                    vehicle_attack_counts[vehicle_id] += 1

                if progress_callback:
                    progress_callback(idx)
            except Exception as e:
                messagebox.showerror("错误",f'处理记录 {idx} 时发生错误: {e}')
                continue
        return results, vehicle_attack_counts

    def analyze_manual_data(self, input_data: Dict):
        # analyze_file_data 已经可以处理单个记录的列表，不需要额外的逻辑
        # 传入一个包含单个字典的列表
        results, _ = self.analyze_file_data([input_data], progress_callback=lambda x: None)
        if results:
            return results[0]
        else:
            raise Exception("手动数据分析未能产生结果。")