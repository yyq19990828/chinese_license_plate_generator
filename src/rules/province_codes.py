"""
省份编码管理模块
基于 GA 36-2018 标准实现的中国省份简称及编码管理
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class ProvinceInfo(BaseModel):
    """省份信息数据结构"""
    name: str  # 省份全称
    abbreviation: str  # 省份简称（车牌上使用的汉字）
    code: int  # 序号（1-31）


class ProvinceManager:
    """省份管理器，提供省份编码相关的操作"""
    
    # 完整的省份信息映射表（基于GA 36-2018标准）
    PROVINCES: Dict[str, ProvinceInfo] = {
        "京": ProvinceInfo(name="北京市", abbreviation="京", code=1),
        "津": ProvinceInfo(name="天津市", abbreviation="津", code=2),
        "冀": ProvinceInfo(name="河北省", abbreviation="冀", code=3),
        "晋": ProvinceInfo(name="山西省", abbreviation="晋", code=4),
        "蒙": ProvinceInfo(name="内蒙古自治区", abbreviation="蒙", code=5),
        "辽": ProvinceInfo(name="辽宁省", abbreviation="辽", code=6),
        "吉": ProvinceInfo(name="吉林省", abbreviation="吉", code=7),
        "黑": ProvinceInfo(name="黑龙江省", abbreviation="黑", code=8),
        "沪": ProvinceInfo(name="上海市", abbreviation="沪", code=9),
        "苏": ProvinceInfo(name="江苏省", abbreviation="苏", code=10),
        "浙": ProvinceInfo(name="浙江省", abbreviation="浙", code=11),
        "皖": ProvinceInfo(name="安徽省", abbreviation="皖", code=12),
        "闽": ProvinceInfo(name="福建省", abbreviation="闽", code=13),
        "赣": ProvinceInfo(name="江西省", abbreviation="赣", code=14),
        "鲁": ProvinceInfo(name="山东省", abbreviation="鲁", code=15),
        "豫": ProvinceInfo(name="河南省", abbreviation="豫", code=16),
        "鄂": ProvinceInfo(name="湖北省", abbreviation="鄂", code=17),
        "湘": ProvinceInfo(name="湖南省", abbreviation="湘", code=18),
        "粤": ProvinceInfo(name="广东省", abbreviation="粤", code=19),
        "桂": ProvinceInfo(name="广西壮族自治区", abbreviation="桂", code=20),
        "琼": ProvinceInfo(name="海南省", abbreviation="琼", code=21),
        "渝": ProvinceInfo(name="重庆市", abbreviation="渝", code=22),
        "川": ProvinceInfo(name="四川省", abbreviation="川", code=23),
        "贵": ProvinceInfo(name="贵州省", abbreviation="贵", code=24),
        "云": ProvinceInfo(name="云南省", abbreviation="云", code=25),
        "藏": ProvinceInfo(name="西藏自治区", abbreviation="藏", code=26),
        "陕": ProvinceInfo(name="陕西省", abbreviation="陕", code=27),
        "甘": ProvinceInfo(name="甘肃省", abbreviation="甘", code=28),
        "青": ProvinceInfo(name="青海省", abbreviation="青", code=29),
        "宁": ProvinceInfo(name="宁夏回族自治区", abbreviation="宁", code=30),
        "新": ProvinceInfo(name="新疆维吾尔自治区", abbreviation="新", code=31),
    }
    
    @classmethod
    def get_all_abbreviations(cls) -> List[str]:
        """获取所有省份简称列表"""
        return list(cls.PROVINCES.keys())
    
    @classmethod
    def get_province_info(cls, abbreviation: str) -> Optional[ProvinceInfo]:
        """
        根据省份简称获取省份信息
        
        Args:
            abbreviation: 省份简称（如"京"、"沪"）
            
        Returns:
            ProvinceInfo对象，如果不存在则返回None
        """
        return cls.PROVINCES.get(abbreviation)
    
    @classmethod
    def is_valid_province(cls, abbreviation: str) -> bool:
        """
        验证省份简称是否合法
        
        Args:
            abbreviation: 省份简称
            
        Returns:
            bool: True表示合法，False表示不合法
        """
        return abbreviation in cls.PROVINCES
    
    @classmethod
    def get_province_by_name(cls, name: str) -> Optional[ProvinceInfo]:
        """
        根据省份全称获取省份信息
        
        Args:
            name: 省份全称（如"北京市"、"上海市"）
            
        Returns:
            ProvinceInfo对象，如果不存在则返回None
        """
        for province_info in cls.PROVINCES.values():
            if province_info.name == name:
                return province_info
        return None
    
    @classmethod
    def get_provinces_by_type(cls, province_type: str = "all") -> List[ProvinceInfo]:
        """
        根据类型获取省份列表
        
        Args:
            province_type: 省份类型
                - "all": 所有省份（默认）
                - "municipality": 直辖市（京、津、沪、渝）
                - "province": 省份
                - "autonomous_region": 自治区
                
        Returns:
            省份信息列表
        """
        all_provinces = list(cls.PROVINCES.values())
        
        if province_type == "all":
            return all_provinces
        elif province_type == "municipality":
            municipalities = ["京", "津", "沪", "渝"]
            return [cls.PROVINCES[abbr] for abbr in municipalities]
        elif province_type == "province":
            # 省份（不含直辖市和自治区）
            provinces = ["冀", "晋", "辽", "吉", "黑", "苏", "浙", "皖", "闽", 
                        "赣", "鲁", "豫", "鄂", "湘", "粤", "琼", "川", "贵", 
                        "云", "陕", "甘", "青"]
            return [cls.PROVINCES[abbr] for abbr in provinces]
        elif province_type == "autonomous_region":
            # 自治区
            autonomous_regions = ["蒙", "桂", "藏", "宁", "新"]
            return [cls.PROVINCES[abbr] for abbr in autonomous_regions]
        else:
            return all_provinces