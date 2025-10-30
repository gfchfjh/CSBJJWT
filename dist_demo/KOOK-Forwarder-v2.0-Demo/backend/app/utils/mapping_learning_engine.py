"""
映射学习引擎 - 基于用户行为学习
功能：
1. 记录用户手动调整的映射
2. 学习常见的映射模式
3. 为相似频道提供更准确的建议
"""
from typing import Dict, List, Tuple
import json
from collections import defaultdict
from datetime import datetime
from ..database import db
from ..utils.logger import logger


class MappingLearningEngine:
    """
    映射学习引擎
    
    通过机器学习用户的映射习惯，提供更准确的智能建议
    """
    
    def __init__(self):
        self.learning_data = defaultdict(list)  # {kook_name@platform: [mappings]}
        self.load_learning_data()
    
    def load_learning_data(self):
        """从数据库加载学习数据"""
        try:
            data_str = db.get_config('mapping_learning_data')
            if data_str:
                raw_data = json.loads(data_str)
                # 转换为defaultdict
                self.learning_data = defaultdict(list, raw_data)
                logger.info(f"✅ 已加载 {len(self.learning_data)} 条映射学习数据")
            else:
                logger.info("ℹ️ 暂无映射学习数据")
        except Exception as e:
            logger.error(f"加载学习数据失败: {str(e)}")
            self.learning_data = defaultdict(list)
    
    def save_learning_data(self):
        """保存学习数据到数据库"""
        try:
            # 转换为普通dict以便序列化
            data_dict = dict(self.learning_data)
            db.set_config('mapping_learning_data', json.dumps(data_dict))
            logger.debug("映射学习数据已保存")
        except Exception as e:
            logger.error(f"保存学习数据失败: {str(e)}")
    
    def learn_from_mapping(self, kook_channel_name: str, target_channel_name: str,
                          target_platform: str, confidence: float = 1.0):
        """
        从用户映射中学习
        
        Args:
            kook_channel_name: KOOK频道名
            target_channel_name: 目标频道名
            target_platform: 目标平台
            confidence: 映射置信度 (0-1)，1.0表示用户手动确认
        """
        # 标准化频道名（去除特殊字符）
        normalized_kook = self._normalize_name(kook_channel_name)
        
        # 映射键: "频道名@平台"
        mapping_key = f"{normalized_kook}@{target_platform}"
        
        # 添加新映射（带权重和时间戳）
        mapping_record = {
            'target_name': target_channel_name,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'original_kook_name': kook_channel_name  # 保留原始名称
        }
        
        self.learning_data[mapping_key].append(mapping_record)
        
        # 保留最近100条记录
        if len(self.learning_data[mapping_key]) > 100:
            self.learning_data[mapping_key] = self.learning_data[mapping_key][-100:]
        
        # 定期保存（每10次学习保存一次）
        if sum(len(v) for v in self.learning_data.values()) % 10 == 0:
            self.save_learning_data()
        
        logger.debug(f"学习映射: {kook_channel_name} → {target_channel_name} ({target_platform}, 置信度={confidence:.2f})")
    
    def get_learned_suggestions(self, kook_channel_name: str, target_platform: str,
                                top_k: int = 5) -> List[Dict]:
        """
        获取基于学习的映射建议
        
        Args:
            kook_channel_name: KOOK频道名
            target_platform: 目标平台
            top_k: 返回前K个建议
            
        Returns:
            [
                {
                    'name': '建议频道名',
                    'confidence': 0.95,
                    'source': 'learned',  # learned/similar/hybrid
                    'reason': '基于历史映射学习',
                    'count': 5  # 映射次数
                },
                ...
            ]
        """
        suggestions = []
        
        normalized_kook = self._normalize_name(kook_channel_name)
        mapping_key = f"{normalized_kook}@{target_platform}"
        
        # 方法1: 完全匹配的学习数据
        if mapping_key in self.learning_data:
            mappings = self.learning_data[mapping_key]
            
            # 统计每个目标频道的映射次数和平均置信度
            target_stats = defaultdict(lambda: {'count': 0, 'total_conf': 0, 'latest_time': None})
            
            for mapping in mappings:
                target_name = mapping['target_name']
                target_stats[target_name]['count'] += 1
                target_stats[target_name]['total_conf'] += mapping.get('confidence', 0.5)
                
                # 记录最新时间
                timestamp = mapping.get('timestamp')
                if timestamp:
                    if target_stats[target_name]['latest_time'] is None or \
                       timestamp > target_stats[target_name]['latest_time']:
                        target_stats[target_name]['latest_time'] = timestamp
            
            # 计算加权置信度
            for target_name, stats in target_stats.items():
                avg_conf = stats['total_conf'] / stats['count']
                
                # 映射次数因子（最多20次映射满分）
                count_factor = min(stats['count'] / 20, 1.0)
                
                # 时间衰减因子（最近的映射权重更高）
                time_factor = self._calculate_time_decay(stats['latest_time'])
                
                # 综合置信度 = 平均置信度(50%) + 次数因子(30%) + 时间因子(20%)
                weighted_conf = (avg_conf * 0.5) + (count_factor * 0.3) + (time_factor * 0.2)
                
                suggestions.append({
                    'name': target_name,
                    'confidence': round(weighted_conf, 3),
                    'source': 'learned',
                    'reason': f'已学习{stats["count"]}次相同映射',
                    'count': stats['count']
                })
        
        # 方法2: 相似频道的映射
        similar_mappings = self._find_similar_mappings(normalized_kook, target_platform, threshold=0.7)
        for mapping in similar_mappings:
            # 相似度衰减：乘以相似度系数
            adjusted_conf = mapping['confidence'] * mapping['similarity'] * 0.85
            
            suggestions.append({
                'name': mapping['target_name'],
                'confidence': round(adjusted_conf, 3),
                'source': 'similar',
                'reason': f'相似频道"{mapping["kook_name"]}"的映射（相似度{mapping["similarity"]:.0%}）',
                'count': mapping.get('count', 1)
            })
        
        # 方法3: 混合匹配（部分关键词匹配）
        keyword_mappings = self._find_keyword_mappings(normalized_kook, target_platform)
        for mapping in keyword_mappings:
            suggestions.append({
                'name': mapping['target_name'],
                'confidence': round(mapping['confidence'] * 0.75, 3),  # 关键词匹配置信度较低
                'source': 'hybrid',
                'reason': f'包含关键词"{mapping["keyword"]}"',
                'count': mapping.get('count', 1)
            })
        
        # 去重（同一个目标名称只保留最高置信度）
        suggestions_map = {}
        for sugg in suggestions:
            name = sugg['name']
            if name not in suggestions_map or sugg['confidence'] > suggestions_map[name]['confidence']:
                suggestions_map[name] = sugg
        
        # 按置信度排序
        final_suggestions = sorted(suggestions_map.values(), 
                                  key=lambda x: x['confidence'], 
                                  reverse=True)
        
        return final_suggestions[:top_k]
    
    def _normalize_name(self, name: str) -> str:
        """标准化频道名"""
        import re
        
        if not name:
            return ""
        
        # 转小写
        name = name.lower()
        
        # 移除特殊字符（保留中文、英文、数字、空格、连字符）
        name = re.sub(r'[^\w\s\-\u4e00-\u9fff]', '', name)
        
        # 移除多余空格
        name = ' '.join(name.split())
        
        return name
    
    def _calculate_time_decay(self, timestamp_str: str) -> float:
        """
        计算时间衰减因子
        
        越近的映射权重越高：
        - 7天内: 1.0
        - 30天内: 0.8
        - 90天内: 0.6
        - 更早: 0.4
        """
        if not timestamp_str:
            return 0.4
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            days_ago = (datetime.now() - timestamp).days
            
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 30:
                return 0.8
            elif days_ago <= 90:
                return 0.6
            else:
                return 0.4
        except:
            return 0.4
    
    def _find_similar_mappings(self, normalized_kook: str, target_platform: str,
                               threshold: float = 0.7) -> List[Dict]:
        """
        查找相似频道的映射
        
        使用编辑距离计算相似度
        """
        from difflib import SequenceMatcher
        
        similar_mappings = []
        
        for mapping_key, mappings in self.learning_data.items():
            # 解析key
            parts = mapping_key.split('@')
            if len(parts) != 2:
                continue
            
            kook_name, platform = parts
            
            # 只考虑相同平台
            if platform != target_platform:
                continue
            
            # 不比较自己
            if kook_name == normalized_kook:
                continue
            
            # 计算相似度
            similarity = SequenceMatcher(None, normalized_kook, kook_name).ratio()
            
            if similarity >= threshold:
                # 统计最常见的映射
                target_counts = defaultdict(int)
                for m in mappings:
                    target_counts[m['target_name']] += 1
                
                if target_counts:
                    most_common_target = max(target_counts.items(), key=lambda x: x[1])
                    
                    similar_mappings.append({
                        'kook_name': kook_name,
                        'target_name': most_common_target[0],
                        'confidence': 0.8,  # 基础置信度
                        'similarity': similarity,
                        'count': most_common_target[1]
                    })
        
        return similar_mappings
    
    def _find_keyword_mappings(self, normalized_kook: str, target_platform: str) -> List[Dict]:
        """
        查找包含关键词的映射
        
        例如："公告频道" 可以匹配 "公告"、"官方公告" 等
        """
        keyword_mappings = []
        
        # 提取关键词（分词）
        keywords = set(normalized_kook.split())
        
        if not keywords:
            return []
        
        for mapping_key, mappings in self.learning_data.items():
            parts = mapping_key.split('@')
            if len(parts) != 2:
                continue
            
            kook_name, platform = parts
            
            if platform != target_platform or kook_name == normalized_kook:
                continue
            
            # 检查是否有关键词匹配
            kook_words = set(kook_name.split())
            common_words = keywords & kook_words
            
            if common_words:
                # 计算关键词匹配度
                match_ratio = len(common_words) / max(len(keywords), len(kook_words))
                
                if match_ratio >= 0.5:  # 至少50%关键词匹配
                    # 统计最常见的映射
                    target_counts = defaultdict(int)
                    for m in mappings:
                        target_counts[m['target_name']] += 1
                    
                    if target_counts:
                        most_common_target = max(target_counts.items(), key=lambda x: x[1])
                        
                        keyword_mappings.append({
                            'target_name': most_common_target[0],
                            'confidence': 0.6 * match_ratio,
                            'keyword': ', '.join(common_words),
                            'count': most_common_target[1]
                        })
        
        return keyword_mappings
    
    def analyze_mapping_quality(self) -> Dict:
        """
        分析映射质量
        
        Returns:
            {
                'total_patterns': 123,  # 学习的映射模式数量
                'high_confidence_patterns': 89,  # 高置信度模式(>0.8)
                'platforms': {
                    'discord': 56,
                    'telegram': 45,
                    'feishu': 22
                },
                'avg_confidence': 0.75,
                'total_mappings': 567,  # 总映射记录数
                'most_common_mappings': [...]  # 最常见的映射
            }
        """
        total_patterns = len(self.learning_data)
        high_conf = 0
        platform_counts = defaultdict(int)
        total_conf = 0
        conf_count = 0
        total_mappings = 0
        mapping_frequencies = defaultdict(int)
        
        for mapping_key, mappings in self.learning_data.items():
            total_mappings += len(mappings)
            
            # 解析平台
            parts = mapping_key.split('@')
            if len(parts) == 2:
                platform_counts[parts[1]] += 1
            
            # 统计置信度
            for mapping in mappings:
                conf = mapping.get('confidence', 0)
                if conf > 0.8:
                    high_conf += 1
                total_conf += conf
                conf_count += 1
                
                # 统计映射频率
                target = mapping.get('target_name')
                if target:
                    mapping_frequencies[f"{parts[0]} → {target}"] += 1
        
        # 获取最常见的映射（前10个）
        most_common = sorted(mapping_frequencies.items(), 
                           key=lambda x: x[1], 
                           reverse=True)[:10]
        
        return {
            'total_patterns': total_patterns,
            'high_confidence_patterns': high_conf,
            'platforms': dict(platform_counts),
            'avg_confidence': round(total_conf / conf_count, 3) if conf_count > 0 else 0,
            'total_mappings': total_mappings,
            'most_common_mappings': [
                {'mapping': m[0], 'count': m[1]} for m in most_common
            ]
        }
    
    def export_learning_data(self) -> str:
        """
        导出学习数据为JSON
        
        用于备份或迁移
        """
        data = {
            'version': '1.0',
            'export_time': datetime.now().isoformat(),
            'stats': self.analyze_mapping_quality(),
            'data': dict(self.learning_data)
        }
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def import_learning_data(self, json_str: str) -> bool:
        """
        从JSON导入学习数据
        
        Args:
            json_str: JSON字符串
            
        Returns:
            是否成功
        """
        try:
            data = json.loads(json_str)
            
            if 'data' in data:
                self.learning_data = defaultdict(list, data['data'])
                self.save_learning_data()
                
                logger.info(f"✅ 成功导入 {len(self.learning_data)} 条学习数据")
                return True
            else:
                logger.error("导入失败：JSON格式错误")
                return False
                
        except Exception as e:
            logger.error(f"导入学习数据失败: {str(e)}")
            return False


# 创建全局实例
mapping_learning_engine = MappingLearningEngine()
