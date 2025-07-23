"""
发牌机关代号管理模块
基于 GA 36-2018 标准实现的中国地级行政区发牌机关代号管理
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel


class RegionalInfo(BaseModel):
    """地区信息数据结构"""
    province: str  # 省份简称
    city_name: str  # 城市/地区名称
    code: str  # 发牌机关代号（单个字母）
    is_multiple: bool = False  # 是否有多个代号


class RegionalCodeManager:
    """发牌机关代号管理器"""
    
    # 完整的发牌机关代号映射表（基于GA 36-2018标准和plate_rules.md）
    REGIONAL_CODES: Dict[str, List[RegionalInfo]] = {
        "京": [  # 北京市 - 使用A-Z（不含I、O）
            RegionalInfo(province="京", city_name="北京市", code=code)
            for code in "ABCDEFGHJKLMNPQRSTUVWXYZ"
        ],
        "津": [  # 天津市 - 使用A-Z（不含I、O）
            RegionalInfo(province="津", city_name="天津市", code=code)
            for code in "ABCDEFGHJKLMNPQRSTUVWXYZ"
        ],
        "冀": [  # 河北省
            RegionalInfo(province="冀", city_name="石家庄市", code="A"),
            RegionalInfo(province="冀", city_name="唐山市", code="B"),
            RegionalInfo(province="冀", city_name="秦皇岛市", code="C"),
            RegionalInfo(province="冀", city_name="邯郸市", code="D"),
            RegionalInfo(province="冀", city_name="邢台市", code="E"),
            RegionalInfo(province="冀", city_name="保定市", code="F"),
            RegionalInfo(province="冀", city_name="张家口市", code="G"),
            RegionalInfo(province="冀", city_name="承德市", code="H"),
            RegionalInfo(province="冀", city_name="沧州市", code="J"),
            RegionalInfo(province="冀", city_name="廊坊市", code="R"),
            RegionalInfo(province="冀", city_name="衡水市", code="T"),
        ],
        "晋": [  # 山西省
            RegionalInfo(province="晋", city_name="太原市", code="A"),
            RegionalInfo(province="晋", city_name="大同市", code="B"),
            RegionalInfo(province="晋", city_name="阳泉市", code="C"),
            RegionalInfo(province="晋", city_name="长治市", code="D"),
            RegionalInfo(province="晋", city_name="晋城市", code="E"),
            RegionalInfo(province="晋", city_name="朔州市", code="F"),
            RegionalInfo(province="晋", city_name="忻州市", code="H"),
            RegionalInfo(province="晋", city_name="吕梁市", code="J"),
            RegionalInfo(province="晋", city_name="晋中市", code="K"),
            RegionalInfo(province="晋", city_name="临汾市", code="L"),
            RegionalInfo(province="晋", city_name="运城市", code="M"),
        ],
        "蒙": [  # 内蒙古自治区
            RegionalInfo(province="蒙", city_name="呼和浩特市", code="A"),
            RegionalInfo(province="蒙", city_name="包头市", code="B"),
            RegionalInfo(province="蒙", city_name="乌海市", code="C"),
            RegionalInfo(province="蒙", city_name="赤峰市", code="D"),
            RegionalInfo(province="蒙", city_name="呼伦贝尔市", code="E"),
            RegionalInfo(province="蒙", city_name="兴安盟", code="F"),
            RegionalInfo(province="蒙", city_name="通辽市", code="G"),
            RegionalInfo(province="蒙", city_name="锡林郭勒盟", code="H"),
            RegionalInfo(province="蒙", city_name="乌兰察布市", code="J"),
            RegionalInfo(province="蒙", city_name="鄂尔多斯市", code="K"),
            RegionalInfo(province="蒙", city_name="巴彦淖尔市", code="L"),
            RegionalInfo(province="蒙", city_name="阿拉善盟", code="M"),
        ],
        "辽": [  # 辽宁省
            RegionalInfo(province="辽", city_name="沈阳市", code="A"),
            RegionalInfo(province="辽", city_name="大连市", code="B"),
            RegionalInfo(province="辽", city_name="鞍山市", code="C"),
            RegionalInfo(province="辽", city_name="抚顺市", code="D"),
            RegionalInfo(province="辽", city_name="本溪市", code="E"),
            RegionalInfo(province="辽", city_name="丹东市", code="F"),
            RegionalInfo(province="辽", city_name="锦州市", code="G"),
            RegionalInfo(province="辽", city_name="营口市", code="H"),
            RegionalInfo(province="辽", city_name="阜新市", code="J"),
            RegionalInfo(province="辽", city_name="辽阳市", code="K"),
            RegionalInfo(province="辽", city_name="盘锦市", code="L"),
            RegionalInfo(province="辽", city_name="铁岭市", code="M"),
            RegionalInfo(province="辽", city_name="朝阳市", code="N"),
            RegionalInfo(province="辽", city_name="葫芦岛市", code="P"),
        ],
        "吉": [  # 吉林省
            RegionalInfo(province="吉", city_name="长春市", code="A"),
            RegionalInfo(province="吉", city_name="吉林市", code="B"),
            RegionalInfo(province="吉", city_name="四平市", code="C"),
            RegionalInfo(province="吉", city_name="辽源市", code="D"),
            RegionalInfo(province="吉", city_name="通化市", code="E"),
            RegionalInfo(province="吉", city_name="白山市", code="F"),
            RegionalInfo(province="吉", city_name="白城市", code="G"),
            RegionalInfo(province="吉", city_name="延边朝鲜族自治州", code="H"),
            RegionalInfo(province="吉", city_name="松原市", code="J"),
            RegionalInfo(province="吉", city_name="长白山保护开发区", code="K"),
        ],
        "黑": [  # 黑龙江省（哈尔滨有A和L两个代号）
            RegionalInfo(province="黑", city_name="哈尔滨市", code="A", is_multiple=True),
            RegionalInfo(province="黑", city_name="哈尔滨市", code="L", is_multiple=True),
            RegionalInfo(province="黑", city_name="齐齐哈尔市", code="B"),
            RegionalInfo(province="黑", city_name="牡丹江市", code="C"),
            RegionalInfo(province="黑", city_name="佳木斯市", code="D"),
            RegionalInfo(province="黑", city_name="大庆市", code="E"),
            RegionalInfo(province="黑", city_name="伊春市", code="F"),
            RegionalInfo(province="黑", city_name="鸡西市", code="G"),
            RegionalInfo(province="黑", city_name="鹤岗市", code="H"),
            RegionalInfo(province="黑", city_name="双鸭山市", code="J"),
            RegionalInfo(province="黑", city_name="七台河市", code="K"),
            RegionalInfo(province="黑", city_name="绥化市", code="M"),
            RegionalInfo(province="黑", city_name="黑河市", code="N"),
            RegionalInfo(province="黑", city_name="大兴安岭地区", code="P"),
            RegionalInfo(province="黑", city_name="垦区", code="R"),
        ],
        "沪": [  # 上海市 - 使用A-Z（不含I、O）
            RegionalInfo(province="沪", city_name="上海市", code=code)
            for code in "ABCDEFGHJKLMNPQRSTUVWXYZ"
        ],
        "苏": [  # 江苏省
            RegionalInfo(province="苏", city_name="南京市", code="A"),
            RegionalInfo(province="苏", city_name="无锡市", code="B"),
            RegionalInfo(province="苏", city_name="徐州市", code="C"),
            RegionalInfo(province="苏", city_name="常州市", code="D"),
            RegionalInfo(province="苏", city_name="苏州市", code="E"),
            RegionalInfo(province="苏", city_name="南通市", code="F"),
            RegionalInfo(province="苏", city_name="连云港市", code="G"),
            RegionalInfo(province="苏", city_name="淮安市", code="H"),
            RegionalInfo(province="苏", city_name="盐城市", code="J"),
            RegionalInfo(province="苏", city_name="扬州市", code="K"),
            RegionalInfo(province="苏", city_name="镇江市", code="L"),
            RegionalInfo(province="苏", city_name="泰州市", code="M"),
            RegionalInfo(province="苏", city_name="宿迁市", code="N"),
        ],
        "浙": [  # 浙江省
            RegionalInfo(province="浙", city_name="杭州市", code="A"),
            RegionalInfo(province="浙", city_name="宁波市", code="B"),
            RegionalInfo(province="浙", city_name="温州市", code="C"),
            RegionalInfo(province="浙", city_name="绍兴市", code="D"),
            RegionalInfo(province="浙", city_name="湖州市", code="E"),
            RegionalInfo(province="浙", city_name="嘉兴市", code="F"),
            RegionalInfo(province="浙", city_name="金华市", code="G"),
            RegionalInfo(province="浙", city_name="衢州市", code="H"),
            RegionalInfo(province="浙", city_name="台州市", code="J"),
            RegionalInfo(province="浙", city_name="丽水市", code="K"),
            RegionalInfo(province="浙", city_name="舟山市", code="L"),
        ],
        "皖": [  # 安徽省
            RegionalInfo(province="皖", city_name="合肥市", code="A"),
            RegionalInfo(province="皖", city_name="芜湖市", code="B"),
            RegionalInfo(province="皖", city_name="蚌埠市", code="C"),
            RegionalInfo(province="皖", city_name="淮南市", code="D"),
            RegionalInfo(province="皖", city_name="马鞍山市", code="E"),
            RegionalInfo(province="皖", city_name="淮北市", code="F"),
            RegionalInfo(province="皖", city_name="铜陵市", code="G"),
            RegionalInfo(province="皖", city_name="安庆市", code="H"),
            RegionalInfo(province="皖", city_name="黄山市", code="J"),
            RegionalInfo(province="皖", city_name="阜阳市", code="K"),
            RegionalInfo(province="皖", city_name="宿州市", code="L"),
            RegionalInfo(province="皖", city_name="滁州市", code="M"),
            RegionalInfo(province="皖", city_name="六安市", code="N"),
            RegionalInfo(province="皖", city_name="宣城市", code="P"),
            RegionalInfo(province="皖", city_name="池州市", code="R"),
            RegionalInfo(province="皖", city_name="亳州市", code="S"),
        ],
        "闽": [  # 福建省（福州有A和K两个代号）
            RegionalInfo(province="闽", city_name="福州市", code="A", is_multiple=True),
            RegionalInfo(province="闽", city_name="福州市", code="K", is_multiple=True),
            RegionalInfo(province="闽", city_name="莆田市", code="B"),
            RegionalInfo(province="闽", city_name="泉州市", code="C"),
            RegionalInfo(province="闽", city_name="厦门市", code="D"),
            RegionalInfo(province="闽", city_name="漳州市", code="E"),
            RegionalInfo(province="闽", city_name="龙岩市", code="F"),
            RegionalInfo(province="闽", city_name="三明市", code="G"),
            RegionalInfo(province="闽", city_name="南平市", code="H"),
            RegionalInfo(province="闽", city_name="宁德市", code="J"),
        ],
        "赣": [  # 江西省（南昌有A和M两个代号）
            RegionalInfo(province="赣", city_name="南昌市", code="A", is_multiple=True),
            RegionalInfo(province="赣", city_name="南昌市", code="M", is_multiple=True),
            RegionalInfo(province="赣", city_name="赣州市", code="B"),
            RegionalInfo(province="赣", city_name="宜春市", code="C"),
            RegionalInfo(province="赣", city_name="吉安市", code="D"),
            RegionalInfo(province="赣", city_name="上饶市", code="E"),
            RegionalInfo(province="赣", city_name="抚州市", code="F"),
            RegionalInfo(province="赣", city_name="九江市", code="G"),
            RegionalInfo(province="赣", city_name="景德镇市", code="H"),
            RegionalInfo(province="赣", city_name="萍乡市", code="J"),
            RegionalInfo(province="赣", city_name="新余市", code="K"),
            RegionalInfo(province="赣", city_name="鹰潭市", code="L"),
        ],
        "鲁": [  # 山东省（多个城市有多个代号）
            RegionalInfo(province="鲁", city_name="济南市", code="A"),
            RegionalInfo(province="鲁", city_name="青岛市", code="B", is_multiple=True),
            RegionalInfo(province="鲁", city_name="青岛市", code="U", is_multiple=True),
            RegionalInfo(province="鲁", city_name="淄博市", code="C"),
            RegionalInfo(province="鲁", city_name="枣庄市", code="D"),
            RegionalInfo(province="鲁", city_name="东营市", code="E"),
            RegionalInfo(province="鲁", city_name="烟台市", code="F", is_multiple=True),
            RegionalInfo(province="鲁", city_name="烟台市", code="Y", is_multiple=True),
            RegionalInfo(province="鲁", city_name="潍坊市", code="G", is_multiple=True),
            RegionalInfo(province="鲁", city_name="潍坊市", code="V", is_multiple=True),
            RegionalInfo(province="鲁", city_name="济宁市", code="H"),
            RegionalInfo(province="鲁", city_name="泰安市", code="J"),
            RegionalInfo(province="鲁", city_name="威海市", code="K"),
            RegionalInfo(province="鲁", city_name="日照市", code="L"),
            RegionalInfo(province="鲁", city_name="滨州市", code="M"),
            RegionalInfo(province="鲁", city_name="德州市", code="N"),
            RegionalInfo(province="鲁", city_name="省直机关", code="O", is_multiple=True),
            RegionalInfo(province="鲁", city_name="省直机关", code="W", is_multiple=True),
            RegionalInfo(province="鲁", city_name="聊城市", code="P"),
            RegionalInfo(province="鲁", city_name="临沂市", code="Q"),
            RegionalInfo(province="鲁", city_name="菏泽市", code="R"),
            RegionalInfo(province="鲁", city_name="莱芜市", code="S"),
        ],
        "豫": [  # 河南省
            RegionalInfo(province="豫", city_name="郑州市", code="A"),
            RegionalInfo(province="豫", city_name="开封市", code="B"),
            RegionalInfo(province="豫", city_name="洛阳市", code="C"),
            RegionalInfo(province="豫", city_name="平顶山市", code="D"),
            RegionalInfo(province="豫", city_name="安阳市", code="E"),
            RegionalInfo(province="豫", city_name="鹤壁市", code="F"),
            RegionalInfo(province="豫", city_name="新乡市", code="G"),
            RegionalInfo(province="豫", city_name="焦作市", code="H"),
            RegionalInfo(province="豫", city_name="濮阳市", code="J"),
            RegionalInfo(province="豫", city_name="许昌市", code="K"),
            RegionalInfo(province="豫", city_name="漯河市", code="L"),
            RegionalInfo(province="豫", city_name="三门峡市", code="M"),
            RegionalInfo(province="豫", city_name="商丘市", code="N"),
            RegionalInfo(province="豫", city_name="周口市", code="P"),
            RegionalInfo(province="豫", city_name="驻马店市", code="Q"),
            RegionalInfo(province="豫", city_name="南阳市", code="R"),
            RegionalInfo(province="豫", city_name="信阳市", code="S"),
            RegionalInfo(province="豫", city_name="济源市", code="U"),
        ],
        "鄂": [  # 湖北省
            RegionalInfo(province="鄂", city_name="武汉市", code="A"),
            RegionalInfo(province="鄂", city_name="黄石市", code="B"),
            RegionalInfo(province="鄂", city_name="十堰市", code="C"),
            RegionalInfo(province="鄂", city_name="荆州市", code="D"),
            RegionalInfo(province="鄂", city_name="宜昌市", code="E"),
            RegionalInfo(province="鄂", city_name="襄阳市", code="F"),
            RegionalInfo(province="鄂", city_name="鄂州市", code="G"),
            RegionalInfo(province="鄂", city_name="荆门市", code="H"),
            RegionalInfo(province="鄂", city_name="黄冈市", code="J"),
            RegionalInfo(province="鄂", city_name="孝感市", code="K"),
            RegionalInfo(province="鄂", city_name="咸宁市", code="L"),
            RegionalInfo(province="鄂", city_name="仙桃市", code="M"),
            RegionalInfo(province="鄂", city_name="潜江市", code="N"),
            RegionalInfo(province="鄂", city_name="神农架林区", code="P"),
            RegionalInfo(province="鄂", city_name="恩施土家族苗族自治州", code="Q"),
            RegionalInfo(province="鄂", city_name="天门市", code="R"),
            RegionalInfo(province="鄂", city_name="随州市", code="S"),
        ],
        "湘": [  # 湖南省（长沙有A和S两个代号）
            RegionalInfo(province="湘", city_name="长沙市", code="A", is_multiple=True),
            RegionalInfo(province="湘", city_name="长沙市", code="S", is_multiple=True),
            RegionalInfo(province="湘", city_name="株洲市", code="B"),
            RegionalInfo(province="湘", city_name="湘潭市", code="C"),
            RegionalInfo(province="湘", city_name="衡阳市", code="D"),
            RegionalInfo(province="湘", city_name="邵阳市", code="E"),
            RegionalInfo(province="湘", city_name="岳阳市", code="F"),
            RegionalInfo(province="湘", city_name="张家界市", code="G"),
            RegionalInfo(province="湘", city_name="益阳市", code="H"),
            RegionalInfo(province="湘", city_name="常德市", code="J"),
            RegionalInfo(province="湘", city_name="娄底市", code="K"),
            RegionalInfo(province="湘", city_name="郴州市", code="L"),
            RegionalInfo(province="湘", city_name="永州市", code="M"),
            RegionalInfo(province="湘", city_name="怀化市", code="N"),
            RegionalInfo(province="湘", city_name="湘西土家族苗族自治州", code="U"),
        ],
        "渝": [  # 重庆市 - 使用A-Z（不含I、O）
            RegionalInfo(province="渝", city_name="重庆市", code=code)
            for code in "ABCDEFGHJKLMNPQRSTUVWXYZ"
        ],
        "粤": [  # 广东省
            RegionalInfo(province="粤", city_name="广州市", code="A"),
            RegionalInfo(province="粤", city_name="深圳市", code="B"),
            RegionalInfo(province="粤", city_name="珠海市", code="C"),
            RegionalInfo(province="粤", city_name="汕头市", code="D"),
            RegionalInfo(province="粤", city_name="佛山市", code="E", is_multiple=True),
            RegionalInfo(province="粤", city_name="佛山市", code="X", is_multiple=True),
            RegionalInfo(province="粤", city_name="佛山市", code="Y", is_multiple=True),
            RegionalInfo(province="粤", city_name="韶关市", code="F"),
            RegionalInfo(province="粤", city_name="湛江市", code="G"),
            RegionalInfo(province="粤", city_name="肇庆市", code="H"),
            RegionalInfo(province="粤", city_name="江门市", code="J"),
            RegionalInfo(province="粤", city_name="茂名市", code="K"),
            RegionalInfo(province="粤", city_name="惠州市", code="L"),
            RegionalInfo(province="粤", city_name="梅州市", code="M"),
            RegionalInfo(province="粤", city_name="汕尾市", code="N"),
            RegionalInfo(province="粤", city_name="河源市", code="P"),
            RegionalInfo(province="粤", city_name="阳江市", code="Q"),
            RegionalInfo(province="粤", city_name="清远市", code="R"),
            RegionalInfo(province="粤", city_name="东莞市", code="S"),
            RegionalInfo(province="粤", city_name="中山市", code="T"),
            RegionalInfo(province="粤", city_name="潮州市", code="U"),
            RegionalInfo(province="粤", city_name="揭阳市", code="V"),
            RegionalInfo(province="粤", city_name="云浮市", code="W"),
            RegionalInfo(province="粤", city_name="港澳入出境车", code="Z"),
        ],
        "桂": [  # 广西壮族自治区
            RegionalInfo(province="桂", city_name="南宁市", code="A"),
            RegionalInfo(province="桂", city_name="柳州市", code="B"),
            RegionalInfo(province="桂", city_name="桂林市", code="C", is_multiple=True),
            RegionalInfo(province="桂", city_name="桂林市", code="H", is_multiple=True),
            RegionalInfo(province="桂", city_name="梧州市", code="D"),
            RegionalInfo(province="桂", city_name="北海市", code="E"),
            RegionalInfo(province="桂", city_name="崇左市", code="F"),
            RegionalInfo(province="桂", city_name="来宾市", code="G"),
            RegionalInfo(province="桂", city_name="贺州市", code="J"),
            RegionalInfo(province="桂", city_name="玉林市", code="K"),
            RegionalInfo(province="桂", city_name="百色市", code="L"),
            RegionalInfo(province="桂", city_name="河池市", code="M"),
            RegionalInfo(province="桂", city_name="钦州市", code="N"),
            RegionalInfo(province="桂", city_name="防城港市", code="P"),
            RegionalInfo(province="桂", city_name="贵港市", code="R"),
        ],
        "琼": [  # 海南省
            RegionalInfo(province="琼", city_name="海口市", code="A"),
            RegionalInfo(province="琼", city_name="三亚市", code="B"),
            RegionalInfo(province="琼", city_name="琼北", code="C"),
            RegionalInfo(province="琼", city_name="琼南", code="D"),
            RegionalInfo(province="琼", city_name="洋浦经济开发区", code="E"),
            RegionalInfo(province="琼", city_name="儋州", code="F"),
        ],
        "川": [  # 四川省
            RegionalInfo(province="川", city_name="成都市", code="A", is_multiple=True),
            RegionalInfo(province="川", city_name="成都市", code="G", is_multiple=True),
            RegionalInfo(province="川", city_name="绵阳市", code="B"),
            RegionalInfo(province="川", city_name="自贡市", code="C"),
            RegionalInfo(province="川", city_name="攀枝花市", code="D"),
            RegionalInfo(province="川", city_name="泸州市", code="E"),
            RegionalInfo(province="川", city_name="德阳市", code="F"),
            RegionalInfo(province="川", city_name="广元市", code="H"),
            RegionalInfo(province="川", city_name="遂宁市", code="J"),
            RegionalInfo(province="川", city_name="内江市", code="K"),
            RegionalInfo(province="川", city_name="乐山市", code="L"),
            RegionalInfo(province="川", city_name="资阳市", code="M"),
            RegionalInfo(province="川", city_name="宜宾市", code="Q"),
            RegionalInfo(province="川", city_name="南充市", code="R"),
            RegionalInfo(province="川", city_name="达州市", code="S"),
            RegionalInfo(province="川", city_name="雅安市", code="T"),
            RegionalInfo(province="川", city_name="阿坝藏族羌族自治州", code="U"),
            RegionalInfo(province="川", city_name="甘孜藏族自治州", code="V"),
            RegionalInfo(province="川", city_name="凉山彝族自治州", code="W"),
            RegionalInfo(province="川", city_name="广安市", code="X"),
            RegionalInfo(province="川", city_name="巴中市", code="Y"),
            RegionalInfo(province="川", city_name="眉山市", code="Z"),
        ],
        "贵": [  # 贵州省
            RegionalInfo(province="贵", city_name="贵阳市", code="A"),
            RegionalInfo(province="贵", city_name="六盘水市", code="B"),
            RegionalInfo(province="贵", city_name="遵义市", code="C"),
            RegionalInfo(province="贵", city_name="铜仁地区", code="D"),
            RegionalInfo(province="贵", city_name="黔西南布依族苗族自治州", code="E"),
            RegionalInfo(province="贵", city_name="毕节地区", code="F"),
            RegionalInfo(province="贵", city_name="安顺市", code="G"),
            RegionalInfo(province="贵", city_name="黔东南苗族侗族自治州", code="H"),
            RegionalInfo(province="贵", city_name="黔南布依族苗族自治州", code="J"),
        ],
        "云": [  # 云南省
            RegionalInfo(province="云", city_name="昆明市", code="A"),
            RegionalInfo(province="云", city_name="昭通市", code="C"),
            RegionalInfo(province="云", city_name="曲靖市", code="D"),
            RegionalInfo(province="云", city_name="楚雄彝族自治州", code="E"),
            RegionalInfo(province="云", city_name="玉溪市", code="F"),
            RegionalInfo(province="云", city_name="红河哈尼族彝族自治州", code="G"),
            RegionalInfo(province="云", city_name="文山壮族苗族自治州", code="H"),
            RegionalInfo(province="云", city_name="普洱市", code="J"),
            RegionalInfo(province="云", city_name="西双版纳傣族自治州", code="K"),
            RegionalInfo(province="云", city_name="大理白族自治州", code="L"),
            RegionalInfo(province="云", city_name="保山市", code="M"),
            RegionalInfo(province="云", city_name="德宏傣族景颇族自治州", code="N"),
            RegionalInfo(province="云", city_name="丽江市", code="P"),
            RegionalInfo(province="云", city_name="怒江傈僳族自治州", code="Q"),
            RegionalInfo(province="云", city_name="迪庆藏族自治州", code="R"),
            RegionalInfo(province="云", city_name="临沧市", code="S"),
        ],
        "藏": [  # 西藏自治区
            RegionalInfo(province="藏", city_name="拉萨市", code="A"),
            RegionalInfo(province="藏", city_name="昌都地区", code="B"),
            RegionalInfo(province="藏", city_name="山南地区", code="C"),
            RegionalInfo(province="藏", city_name="日喀则地区", code="D"),
            RegionalInfo(province="藏", city_name="那曲地区", code="E"),
            RegionalInfo(province="藏", city_name="阿里地区", code="F"),
            RegionalInfo(province="藏", city_name="林芝地区", code="G"),
        ],
        "陕": [  # 陕西省
            RegionalInfo(province="陕", city_name="西安市", code="A"),
            RegionalInfo(province="陕", city_name="铜川市", code="B"),
            RegionalInfo(province="陕", city_name="宝鸡市", code="C"),
            RegionalInfo(province="陕", city_name="咸阳市", code="D"),
            RegionalInfo(province="陕", city_name="渭南市", code="E"),
            RegionalInfo(province="陕", city_name="汉中市", code="F"),
            RegionalInfo(province="陕", city_name="安康市", code="G"),
            RegionalInfo(province="陕", city_name="商洛市", code="H"),
            RegionalInfo(province="陕", city_name="延安市", code="J"),
            RegionalInfo(province="陕", city_name="榆林市", code="K"),
            RegionalInfo(province="陕", city_name="杨凌", code="V"),
        ],
        "甘": [  # 甘肃省
            RegionalInfo(province="甘", city_name="兰州市", code="A"),
            RegionalInfo(province="甘", city_name="嘉峪关市", code="B"),
            RegionalInfo(province="甘", city_name="金昌市", code="C"),
            RegionalInfo(province="甘", city_name="白银市", code="D"),
            RegionalInfo(province="甘", city_name="天水市", code="E"),
            RegionalInfo(province="甘", city_name="酒泉市", code="F"),
            RegionalInfo(province="甘", city_name="张掖市", code="G"),
            RegionalInfo(province="甘", city_name="武威市", code="H"),
            RegionalInfo(province="甘", city_name="定西市", code="J"),
            RegionalInfo(province="甘", city_name="陇南市", code="K"),
            RegionalInfo(province="甘", city_name="平凉市", code="L"),
            RegionalInfo(province="甘", city_name="庆阳市", code="M"),
            RegionalInfo(province="甘", city_name="临夏回族自治州", code="N"),
            RegionalInfo(province="甘", city_name="甘南藏族自治州", code="P"),
        ],
        "青": [  # 青海省
            RegionalInfo(province="青", city_name="西宁市", code="A"),
            RegionalInfo(province="青", city_name="海东地区", code="B"),
            RegionalInfo(province="青", city_name="海北藏族自治州", code="C"),
            RegionalInfo(province="青", city_name="黄南藏族自治州", code="D"),
            RegionalInfo(province="青", city_name="海南藏族自治州", code="E"),
            RegionalInfo(province="青", city_name="果洛藏族自治州", code="F"),
            RegionalInfo(province="青", city_name="玉树藏族自治州", code="G"),
            RegionalInfo(province="青", city_name="海西蒙古族藏族自治州", code="H"),
        ],
        "宁": [  # 宁夏回族自治区
            RegionalInfo(province="宁", city_name="银川市", code="A"),
            RegionalInfo(province="宁", city_name="石嘴山市", code="B"),
            RegionalInfo(province="宁", city_name="吴忠市", code="C"),
            RegionalInfo(province="宁", city_name="固原市", code="D"),
            RegionalInfo(province="宁", city_name="中卫市", code="E"),
        ],
        "新": [  # 新疆维吾尔自治区
            RegionalInfo(province="新", city_name="乌鲁木齐市", code="A"),
            RegionalInfo(province="新", city_name="昌吉回族自治州", code="B"),
            RegionalInfo(province="新", city_name="石河子市", code="C"),
            RegionalInfo(province="新", city_name="伊犁哈萨克自治州", code="D", is_multiple=True),
            RegionalInfo(province="新", city_name="博尔塔拉蒙古自治州", code="E"),
            RegionalInfo(province="新", city_name="伊犁哈萨克自治州", code="F", is_multiple=True),
            RegionalInfo(province="新", city_name="塔城地区", code="G"),
            RegionalInfo(province="新", city_name="阿勒泰地区", code="H"),
            RegionalInfo(province="新", city_name="克拉玛依市", code="J"),
            RegionalInfo(province="新", city_name="吐鲁番地区", code="K"),
            RegionalInfo(province="新", city_name="哈密地区", code="L"),
            RegionalInfo(province="新", city_name="巴音郭楞蒙古自治州", code="M"),
            RegionalInfo(province="新", city_name="阿克苏地区", code="N"),
            RegionalInfo(province="新", city_name="克孜勒苏柯尔克孜自治州", code="P"),
            RegionalInfo(province="新", city_name="喀什地区", code="Q"),
            RegionalInfo(province="新", city_name="和田地区", code="R"),
        ],
    }
    
    @classmethod
    def get_regional_codes(cls, province: str) -> List[RegionalInfo]:
        """
        获取指定省份的所有发牌机关代号
        
        Args:
            province: 省份简称
            
        Returns:
            该省份的所有发牌机关代号信息列表
        """
        return cls.REGIONAL_CODES.get(province, [])
    
    @classmethod
    def get_all_codes_for_province(cls, province: str) -> List[str]:
        """
        获取指定省份的所有发牌机关代号字母
        
        Args:
            province: 省份简称
            
        Returns:
            该省份的所有代号字母列表
        """
        regional_infos = cls.get_regional_codes(province)
        return [info.code for info in regional_infos]
    
    @classmethod
    def is_valid_regional_code(cls, province: str, code: str) -> bool:
        """
        验证省份和发牌机关代号的组合是否合法
        
        Args:
            province: 省份简称
            code: 发牌机关代号
            
        Returns:
            bool: True表示合法，False表示不合法
        """
        valid_codes = cls.get_all_codes_for_province(province)
        return code in valid_codes
    
    @classmethod
    def get_city_info(cls, province: str, code: str) -> Optional[RegionalInfo]:
        """
        根据省份和发牌机关代号获取城市信息
        
        Args:
            province: 省份简称
            code: 发牌机关代号
            
        Returns:
            RegionalInfo对象，如果不存在则返回None
        """
        regional_infos = cls.get_regional_codes(province)
        for info in regional_infos:
            if info.code == code:
                return info
        return None
    
    @classmethod
    def get_available_codes(cls, exclude_io: bool = True) -> Set[str]:
        """
        获取所有可用的发牌机关代号字母
        
        Args:
            exclude_io: 是否排除I和O字母（默认True，符合GA标准）
            
        Returns:
            可用代号字母集合
        """
        if exclude_io:
            return set("ABCDEFGHJKLMNPQRSTUVWXYZ")
        else:
            return set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")