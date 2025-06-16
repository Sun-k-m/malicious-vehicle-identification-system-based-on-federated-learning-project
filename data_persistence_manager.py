import random
import json
import datetime
from pathlib import Path
from typing import Dict, List

class DataPersistenceManager:
    def __init__(self, data_file="saved_records.json"):
        """
            初始化数据持久化管理器。

            data_file: 存储数据的文件名，默认为"saved_records.json"。
        """
        self.data_file = base_path / data_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """确保数据文件存在，如果不存在则创建空列表"""
        if not self.data_file.exists():
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)

    def save_record(self, record: Dict):
        """保存单条记录到JSON文件"""
        with open(self.data_file, 'r+', encoding='utf-8') as f:
            file_data = json.load(f)
            file_data.append(record)
            f.seek(0)
            json.dump(file_data, f, indent=4)
            f.truncate()

    def get_last_record(self) -> Dict:
        """从文件中读取最后一条记录"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
            if records:
                return records[-1]
            raise ValueError("没有找到任何保存的记录。")

    def generate_complete_record(self, input_data: Dict) -> Dict:
        """
        根据手动输入生成完整的记录，补充默认值和时间戳。
        """
        complete_record = input_data.copy()

        # 补充默认字段
        complete_record.setdefault("type", "CAM")
        complete_record.setdefault("sender", "ManualInput")
        complete_record.setdefault("senderPseudo", "ManualUser")
        complete_record.setdefault("exchangedMessageType", "CAM")
        complete_record.setdefault("EventID", 0)
        complete_record.setdefault("EventType", "Normal")
        complete_record.setdefault("RoadID", "Unknown")
        complete_record.setdefault("hazardOccurrence", False)
        complete_record.setdefault("messageID", f"MSG_{random.randint(10000, 99999)}")
        complete_record.setdefault("vehicleId", f"VEH_{random.randint(1000, 9999)}")

        # 添加时间戳
        current_time = datetime.datetime.now().isoformat()
        complete_record.setdefault("rcvTime", current_time)
        complete_record.setdefault("sendTime", current_time)
        complete_record.setdefault("savedTimestamp", current_time)

        return complete_record

    def load_json_data(self, filepath) -> List[Dict]:
        """从指定JSON文件加载数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            records = json.load(f)
        return records

base_path = Path(__file__).parent