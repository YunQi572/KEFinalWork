-- 创建知识图谱三元组表
CREATE TABLE knowledge_triples (
                                   id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                   head_entity VARCHAR(255) NOT NULL,
                                   relation VARCHAR(255) NOT NULL,
                                   tail_entity VARCHAR(255) NOT NULL,
                                   relation_property TEXT,
                                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建关系类型约束表
CREATE TABLE valid_relations (
                                 id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                 relation_name VARCHAR(255) UNIQUE NOT NULL
);

-- 初始化允许的关系类型
INSERT INTO valid_relations (relation_name) VALUES
                                                ('是'), ('位于'), ('隶属于'), ('属于类型'), ('用于诊断'), ('影响扩散'),
                                                ('下设于'), ('依托于'), ('供职于'), ('属于领域'), ('用于'), ('参与'),
                                                ('属于手段'), ('导致改变'), ('属于工具'), ('属于过程'), ('随后是'),
                                                ('被传播_by'), ('携带'), ('发育于'), ('侵染'), ('发展为'), ('恶化为'),
                                                ('表现为'), ('搭载'), ('通过分析'), ('实现'), ('通过计算'), ('产生'),
                                                ('增强'), ('影响'), ('制约'), ('于时间监测'), ('构成'),
                                                ('针对'), ('利用'), ('控制'), ('应用于'), ('处理'), ('决定'), ('造成'),
                                                ('削弱'), ('关联'), ('需要'), ('HOST_OF'), ('VECTOR_OF'), ('USES_METHOD'),
                                                ('OCCURS_IN'), ('DISTRIBUTED_IN'), ('CONTROLLED_BY'), ('RESEARCHED_BY'),
                                                ('CONDUCTED_BY'), ('AFFILIATED_WITH'), ('IS_A'), ('AFFECTS'), ('HAS_RISK'),
                                                ('MENTIONED_IN'), ('STUDIED_IN'), ('NEXT_PERIOD'), ('AUTHORED'),
                                                ('RESEARCHED_IN'), ('STUDIED'), ('USED_FOR'), ('EVOLVED_TO'), ('PIONEERED'),
                                                ('LED'), ('AWARDED'), ('TEACHES'), ('USED_IN'), ('OCCURRED_IN'),
                                                ('FOUND_IN'), ('PART_OF'), ('TAUGHT'), ('COOPERATED_WITH'), ('REGULATES'),
                                                ('LEADS_TO'), ('ORGANIZED'), ('由病原引起'), ('是主要传播媒介'), ('是主要寄主'),
                                                ('是寄主'), ('是天敌'), ('有发生'), ('属于机构'), ('是时间点'), ('危害'),
                                                ('用于防治'), ('是防治方法'), ('可减轻'), ('有生态位重叠'), ('影响种群密度'),
                                                ('撰写'), ('专业是'), ('发现新物种'), ('创建评价体系'), ('用于预测种群密度'),
                                                ('可寄生'), ('寄生率可达'), ('单头可防治3到4头幼虫'), ('单头可感染4株树'),
                                                ('授予博士学位'), ('由何引起'), ('通过什么传播'), ('分布于'), ('使用技术'),
                                                ('控制合成'), ('提供'), ('是什么的必要条件'), ('促进'),
                                                ('具有特性'), ('具有'), ('完成于'), ('发生于'), ('属于'), ('担任'),
                                                ('用于预防'), ('通过媒介'), ('通过方式'), ('是新传播媒介'), ('是新传播途径'),
                                                ('提供底物'), ('调控表达');

-- === 1. 基础实体关系 ===
-- 省份归类
INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT provName, '是', '省份'
FROM (SELECT '山东省' AS provName UNION SELECT '辽宁省' UNION SELECT '安徽省' UNION SELECT '江苏省'
      UNION SELECT '浙江省' UNION SELECT '福建省' UNION SELECT '江西省' UNION SELECT '湖南省'
      UNION SELECT '湖北省' UNION SELECT '广东省' UNION SELECT '广西' UNION SELECT '四川'
      UNION SELECT '云南' UNION SELECT '贵州' UNION SELECT '陕西省' UNION SELECT '甘肃省'
      UNION SELECT '宁夏' UNION SELECT '青海' UNION SELECT '新疆' UNION SELECT '黑龙江省'
      UNION SELECT '吉林省' UNION SELECT '内蒙古' UNION SELECT '河北省' UNION SELECT '河南省'
      UNION SELECT '山西省' UNION SELECT '北京' UNION SELECT '天津' UNION SELECT '上海'
      UNION SELECT '重庆' UNION SELECT '台湾') AS provinces;

-- 城市归类
INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT cityName, '是', '城市'
FROM (SELECT '泰安市' AS cityName UNION SELECT '威海市' UNION SELECT '烟台' UNION SELECT '青岛'
      UNION SELECT '淄博' UNION SELECT '黄山市' UNION SELECT '合肥' UNION SELECT '南京'
      UNION SELECT '杭州' UNION SELECT '宁波' UNION SELECT '广州' UNION SELECT '昆明'
      UNION SELECT '成都' UNION SELECT '武汉' UNION SELECT '西安' UNION SELECT '沈阳'
      UNION SELECT '哈尔滨' UNION SELECT '乌鲁木齐' UNION SELECT '兰州' UNION SELECT '西宁'
      UNION SELECT '银川' UNION SELECT '呼和浩特' UNION SELECT '拉萨' UNION SELECT '南宁'
      UNION SELECT '海口' UNION SELECT '大连市' UNION SELECT '马鞍山市' UNION SELECT '邻水市'
      UNION SELECT '仁怀市') AS cities;

-- 地理包含关系
INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT loc, '位于', '山东省'
FROM (SELECT '泰安市' AS loc UNION SELECT '威海市' UNION SELECT '烟台' UNION SELECT '青岛'
      UNION SELECT '淄博' UNION SELECT '济南' UNION SELECT '泰山' UNION SELECT '泰山风景区'
      UNION SELECT '崂山区' UNION SELECT '荣成' UNION SELECT '长岛') AS locations;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT loc, '位于', '泰安市'
FROM (SELECT '泰山' AS loc UNION SELECT '泰山风景区' UNION SELECT '天烛峰' UNION SELECT '桃花峪'
      UNION SELECT '玉泉寺' UNION SELECT '红门' UNION SELECT '中天门' UNION SELECT '南天门'
      UNION SELECT '灵岩寺' UNION SELECT '大津口乡' UNION SELECT '樱桃园' UNION SELECT '竹林寺') AS locations;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('沈阳', '位于', '辽宁省'),
                                                                       ('大连市', '位于', '辽宁省'),
                                                                       ('抚顺市', '位于', '辽宁省'),
                                                                       ('丹东', '位于', '辽宁省'),
                                                                       ('合肥', '位于', '安徽省'),
                                                                       ('黄山市', '位于', '安徽省'),
                                                                       ('马鞍山市', '位于', '安徽省'),
                                                                       ('巢湖市', '位于', '安徽省'),
                                                                       ('六安市', '位于', '安徽省'),
                                                                       ('霍山县', '位于', '安徽省'),
                                                                       ('九华山', '位于', '安徽省'),
                                                                       ('西安', '位于', '陕西省'),
                                                                       ('柞水县', '位于', '陕西省'),
                                                                       ('佛坪县', '位于', '陕西省');

-- 大区域关系
INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT prov, '位于', '中国'
FROM (SELECT '山东省' AS prov UNION SELECT '辽宁省' UNION SELECT '安徽省' UNION SELECT '江苏省'
      UNION SELECT '浙江省' UNION SELECT '福建省' UNION SELECT '江西省' UNION SELECT '湖南省'
      UNION SELECT '湖北省' UNION SELECT '广东省' UNION SELECT '广西' UNION SELECT '四川'
      UNION SELECT '云南' UNION SELECT '贵州' UNION SELECT '陕西省' UNION SELECT '甘肃省'
      UNION SELECT '宁夏' UNION SELECT '青海' UNION SELECT '新疆' UNION SELECT '北京'
      UNION SELECT '天津' UNION SELECT '上海' UNION SELECT '重庆' UNION SELECT '台湾') AS provinces;

-- === 2. 寄主植物和昆虫归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT tree, '隶属于', '松属'
FROM (SELECT '马尾松' AS tree UNION SELECT '油松' UNION SELECT '赤松' UNION SELECT '黑松'
      UNION SELECT '华山松' UNION SELECT '白皮松' UNION SELECT '黄山松' UNION SELECT '湿地松'
      UNION SELECT '火炬松' UNION SELECT '红松' UNION SELECT '云南松' UNION SELECT '五针松') AS trees;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT tree, '属于类型', '阔叶树'
FROM (SELECT '法桐' AS tree UNION SELECT '梧桐' UNION SELECT '白蜡' UNION SELECT '桑树'
      UNION SELECT '臭椿' UNION SELECT '香椿' UNION SELECT '白桦' UNION SELECT '榆树'
      UNION SELECT '杨属' UNION SELECT '柳树' UNION SELECT '枫杨' UNION SELECT '泡桐') AS trees;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT bug, '隶属于', '天牛'
FROM (SELECT '松墨天牛' AS bug UNION SELECT '松褐天牛' UNION SELECT '褐幽天牛' UNION SELECT '短角幽天牛') AS bugs;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT bug, '属于类型', '天敌昆虫'
FROM (SELECT '花绒坚甲' AS bug UNION SELECT '花绒寄甲' UNION SELECT '管氏肿腿蜂' UNION SELECT '肿腿蜂'
      UNION SELECT '赤眼蜂' UNION SELECT '金小蜂' UNION SELECT '黑卵蜂' UNION SELECT '白蛾周氏啮小蜂'
      UNION SELECT '大红瓢虫' UNION SELECT '莱氏猛叩甲') AS bugs;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('Bursaphelenchus xylophilus', '属于类型', '线虫'),
                                                                       ('白僵菌', '属于类型', '真菌'),
                                                                       ('球孢白僵菌', '属于类型', '真菌'),
                                                                       ('布氏白僵菌', '属于类型', '真菌'),
                                                                       ('金龟子绿僵菌', '属于类型', '真菌');

-- === 3. 机构与人员关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('植物保护学院', '下设于', '山东农业大学'),
                                                                       ('森林保护学国家林业局重点实验室', '依托于', '中国林业科学研究院');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('申卫星', '供职于', '山东农业大学'),
                                                                       ('黄大卫', '供职于', '山东农业大学'),
                                                                       ('刘同先', '供职于', '山东农业大学'),
                                                                       ('张星耀', '供职于', '中国林业科学研究院'),
                                                                       ('杨忠岐', '供职于', '中国林业科学研究院'),
                                                                       ('展茂魁', '供职于', '中国林业科学研究院'),
                                                                       ('王小艺', '供职于', '中国林业科学研究院'),
                                                                       ('叶建仁', '供职于', '南京林业大学'),
                                                                       ('陈凤毛', '供职于', '南京林业大学');

-- === 4. 技术与算法归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT algo, '属于类型', '算法'
FROM (SELECT '随机森林' AS algo UNION SELECT '支持向量机' UNION SELECT '线性判别分析'
      UNION SELECT '竞争性自适应重加权算法' UNION SELECT '连续投影算法' UNION SELECT '人工神经网络') AS algorithms;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT tech, '属于领域', '遥感技术'
FROM (SELECT '高光谱遥感' AS tech UNION SELECT '无人机高光谱' UNION SELECT 'Sentinel-2卫星影像' UNION SELECT '多光谱遥感') AS technologies;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT tech, '属于领域', '分子生物学技术'
FROM (SELECT 'PCR检测' AS tech UNION SELECT '实时荧光定量PCR' UNION SELECT 'qRT-PCR' UNION SELECT '转录组测序'
      UNION SELECT 'RNA干扰' UNION SELECT '基因克隆') AS technologies;

-- === 5. 时间关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
SELECT year_name, '是', '年份'
FROM (SELECT '2019年' AS year_name UNION SELECT '2020年' UNION SELECT '2021年'
      UNION SELECT '2022年' UNION SELECT '2023年') AS years;

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('2019年', '随后是', '2020年'),
                                                                       ('2020年', '随后是', '2021年'),
                                                                       ('2021年', '随后是', '2022年'),
                                                                       ('2022年', '随后是', '2023年');

-- === 6. 症状与诊断关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('叶片失水、萎缩、变黄变红', '用于诊断', '诊断'),
                                                                       ('树脂分泌减少', '用于诊断', '诊断'),
                                                                       ('针叶变黄变红', '用于诊断', '诊断'),
                                                                       ('高温', '影响扩散', '松材线虫病'),
                                                                       ('干旱', '影响扩散', '松材线虫病'),
                                                                       ('降水', '影响扩散', '松材线虫病');

-- === 7. 病害归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松苗猝倒病', '属于类型', '病害'),
                                                                       ('落叶松早期落叶病', '属于类型', '病害'),
                                                                       ('油茶炭疽病', '属于类型', '病害'),
                                                                       ('杨树腐烂病', '属于类型', '病害'),
                                                                       ('毛竹枯梢病', '属于类型', '病害'),
                                                                       ('松针褐斑病', '属于类型', '病害'),
                                                                       ('泡桐丛枝病', '属于类型', '病害'),
                                                                       ('松树溃疡病', '属于类型', '病害'),
                                                                       ('松树枯梢病', '属于类型', '病害'),
                                                                       ('松树锈病', '属于类型', '病害'),
                                                                       ('松树白粉病', '属于类型', '病害'),
                                                                       ('松树赤枯病', '属于类型', '病害'),
                                                                       ('松树赤落叶病', '属于类型', '病害'),
                                                                       ('松树赤星病', '属于类型', '病害'),
                                                                       ('松树赤锈病', '属于类型', '病害'),
                                                                       ('松树黄萎病', '属于类型', '病害'),
                                                                       ('松树褐斑病', '属于类型', '病害'),
                                                                       ('松树黑斑病', '属于类型', '病害'),
                                                                       ('松树黑星病', '属于类型', '病害'),
                                                                       ('松树黑腐病', '属于类型', '病害'),
                                                                       ('松树黑痣病', '属于类型', '病害'),
                                                                       ('苹果树腐烂病', '属于类型', '病害'),
                                                                       ('油桐叶斑病', '属于类型', '病害'),
                                                                       ('油桐枯萎病', '属于类型', '病害'),
                                                                       ('银杏茎腐病', '属于类型', '病害'),
                                                                       ('杨苗黑斑病', '属于类型', '病害'),
                                                                       ('杨树灰斑病', '属于类型', '病害'),
                                                                       ('泡桐实生苗炭疽病', '属于类型', '病害'),
                                                                       ('毛白杨锈病', '属于类型', '病害'),
                                                                       ('落叶松枯梢病', '属于类型', '病害'),
                                                                       ('红松疱锈病', '属于类型', '病害'),
                                                                       ('杉木炭疽病', '属于类型', '病害'),
                                                                       ('杉木细菌性叶枯病', '属于类型', '病害'),
                                                                       ('油橄榄孔雀斑病', '属于类型', '病害'),
                                                                       ('油橄榄青枯病', '属于类型', '病害'),
                                                                       ('杨树溃疡病', '属于类型', '病害'),
                                                                       ('松杉苗木猝倒病', '属于类型', '病害'),
                                                                       ('杨树叶锈病', '属于类型', '病害'),
                                                                       ('油桐黑斑病', '属于类型', '病害'),
                                                                       ('竹杆锈病', '属于类型', '病害'),
                                                                       ('杨黑斑病', '属于类型', '病害'),
                                                                       ('松杨栅锈病', '属于类型', '病害'),
                                                                       ('松树萎蔫病', '属于类型', '病害'),
                                                                       ('石榴溃疡病', '属于类型', '病害'),
                                                                       ('欧美杨疸病', '属于类型', '病害'),
                                                                       ('核桃基腐病', '属于类型', '病害'),
                                                                       ('五针松疱病', '属于类型', '病害'),
                                                                       ('板栗褐绿叶枯病', '属于类型', '病害'),
                                                                       ('马褂木褐斑病', '属于类型', '病害'),
                                                                       ('红枝鸡爪槭枝枯病', '属于类型', '病害'),
                                                                       ('枣疯病', '属于类型', '病害');

-- === 8. 农药与药剂归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('杀螟松', '属于类型', '农药药剂'),
                                                                       ('保松灵', '属于类型', '农药药剂'),
                                                                       ('阿维菌素', '属于类型', '农药药剂'),
                                                                       ('噻虫啉', '属于类型', '农药药剂'),
                                                                       ('苦参碱', '属于类型', '农药药剂'),
                                                                       ('烟碱', '属于类型', '农药药剂'),
                                                                       ('苏云金杆菌', '属于类型', '农药药剂'),
                                                                       ('青虫菌', '属于类型', '农药药剂'),
                                                                       ('微生物杀虫剂', '属于类型', '农药药剂'),
                                                                       ('病毒杀虫剂', '属于类型', '农药药剂'),
                                                                       ('细菌杀虫剂', '属于类型', '农药药剂'),
                                                                       ('真菌杀虫剂', '属于类型', '农药药剂'),
                                                                       ('抗生素', '属于类型', '农药药剂'),
                                                                       ('昆虫生长调节剂', '属于类型', '农药药剂'),
                                                                       ('植物源农药', '属于类型', '农药药剂'),
                                                                       ('矿物源农药', '属于类型', '农药药剂'),
                                                                       ('引诱剂', '属于类型', '农药药剂'),
                                                                       ('熏蒸剂', '属于类型', '农药药剂');

-- === 9. 研究模型与软件归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('CLIMEX', '属于工具', '研究模型与软件'),
                                                                       ('@risk', '属于工具', '研究模型与软件'),
                                                                       ('GARP', '属于工具', '研究模型与软件'),
                                                                       ('MAXENT', '属于工具', '研究模型与软件'),
                                                                       ('DIVA-GIS', '属于工具', '研究模型与软件'),
                                                                       ('ArcView GIS', '属于工具', '研究模型与软件'),
                                                                       ('BIOCLIM', '属于工具', '研究模型与软件'),
                                                                       ('生态位模型', '属于工具', '研究模型与软件'),
                                                                       ('种群动态模型', '属于工具', '研究模型与软件'),
                                                                       ('生命表', '属于工具', '研究模型与软件'),
                                                                       ('风险评价矩阵', '属于工具', '研究模型与软件');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('CLIMEX', '用于', '风险评估'),
                                                                       ('@risk', '用于', '风险评估'),
                                                                       ('GARP', '用于', '风险评估'),
                                                                       ('MAXENT', '用于', '风险评估'),
                                                                       ('风险评价矩阵', '用于', '风险评估');

-- === 10. 基因归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('Hccs', '是', '基因'),
                                                                       ('Pcyt1', '是', '基因'),
                                                                       ('Ran基因', '是', '基因'),
                                                                       ('细胞色素c血红素裂合酶基因', '是', '基因'),
                                                                       ('磷脂酰胆碱胞苷酰转移酶基因', '是', '基因'),
                                                                       ('GTP结合核蛋白Ran', '是', '基因');

-- === 11. 代谢通路归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('氧化磷酸化', '属于过程', '代谢通路'),
                                                                       ('脂肪酸β-氧化', '属于过程', '代谢通路'),
                                                                       ('三羧酸循环', '属于过程', '代谢通路'),
                                                                       ('糖酵解', '属于过程', '代谢通路'),
                                                                       ('糖异生', '属于过程', '代谢通路'),
                                                                       ('脂肪代谢', '属于过程', '代谢通路'),
                                                                       ('能量代谢', '属于过程', '代谢通路');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('Hccs', '参与', '氧化磷酸化'),
                                                                       ('Pcyt1', '参与', '脂肪代谢');

-- === 12. 防治手段归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('疫木清理', '属于手段', '物理防治'),
                                                                       ('焚烧处理', '属于手段', '物理防治'),
                                                                       ('诱捕器', '属于手段', '物理防治'),
                                                                       ('频振式杀虫灯', '属于手段', '物理防治'),
                                                                       ('自动虫情测报灯', '属于手段', '物理防治'),
                                                                       ('人工物理隔离', '属于手段', '物理防治'),
                                                                       ('热处理', '属于手段', '物理防治'),
                                                                       ('微波处理', '属于手段', '物理防治'),
                                                                       ('飞机防治', '属于手段', '化学防治'),
                                                                       ('树干注射', '属于手段', '化学防治'),
                                                                       ('喷雾', '属于手段', '化学防治'),
                                                                       ('喷粉', '属于手段', '化学防治'),
                                                                       ('熏蒸', '属于手段', '化学防治'),
                                                                       ('毒环', '属于手段', '化学防治'),
                                                                       ('毒饵', '属于手段', '化学防治'),
                                                                       ('烟剂', '属于手段', '化学防治'),
                                                                       ('粉剂', '属于手段', '化学防治'),
                                                                       ('乳剂', '属于手段', '化学防治'),
                                                                       ('悬浮剂', '属于手段', '化学防治'),
                                                                       ('缓释剂', '属于手段', '化学防治'),
                                                                       ('营林措施', '属于手段', '营林防治'),
                                                                       ('修枝间伐', '属于手段', '营林防治'),
                                                                       ('卫生伐', '属于手段', '营林防治'),
                                                                       ('修枝', '属于手段', '营林防治'),
                                                                       ('间伐', '属于手段', '营林防治'),
                                                                       ('封山育林', '属于手段', '营林防治'),
                                                                       ('混交林', '属于手段', '营林防治'),
                                                                       ('抚育管理', '属于手段', '营林防治'),
                                                                       ('树种改造', '属于手段', '营林防治'),
                                                                       ('检疫封锁', '属于手段', '检疫措施'),
                                                                       ('检疫检查站', '属于手段', '检疫措施'),
                                                                       ('执法检查', '属于手段', '检疫措施'),
                                                                       ('产地检疫', '属于手段', '检疫措施'),
                                                                       ('调运检疫', '属于手段', '检疫措施');

-- === 13. 生理指标归类 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('叶绿素含量', '是', '生理指标'),
                                                                       ('叶绿素a含量', '是', '生理指标'),
                                                                       ('叶绿素b含量', '是', '生理指标'),
                                                                       ('类胡萝卜素含量', '是', '生理指标'),
                                                                       ('叶片含水率', '是', '生理指标'),
                                                                       ('光合速率', '是', '生理指标'),
                                                                       ('蒸腾速率', '是', '生理指标'),
                                                                       ('气孔导度', '是', '生理指标'),
                                                                       ('胞间CO2浓度', '是', '生理指标');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', '导致改变', '叶绿素含量'),
                                                                       ('松材线虫病', '导致改变', '叶片含水率'),
                                                                       ('松材线虫病', '导致改变', '光合作用');

-- === 14. 病原与媒介昆虫关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('松材线虫', '被传播_by', '松墨天牛', '{"机制": "媒介昆虫携带"}'),
                                                                                          ('松墨天牛', '携带', '松材线虫', '{"部位": "气管系统"}'),
                                                                                          ('松墨天牛', '发育于', '蛹室', '{"阶段": "蛹期"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('松材线虫', '侵染', '马尾松', '{"方式": "伤口侵入"}'),
                                                                                          ('松材线虫', '侵染', '赤松', '{"方式": "伤口侵入"}'),
                                                                                          ('松材线虫', '侵染', '红松', '{"方式": "伤口侵入"}'),
                                                                                          ('松材线虫', '侵染', '黑松', '{"方式": "伤口侵入"}'),
                                                                                          ('松材线虫', '侵染', '黄山松', '{"方式": "伤口侵入"}');

-- === 15. 病害发展阶段 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('早期感病', '发展为', '中期感病', '{"时间框架": "2-4周"}'),
                                                                                          ('中期感病', '恶化为', '晚期感病', '{"时间框架": "4-8周"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('早期感病', '表现为', '树脂分泌减少', '{"显著度": "高"}'),
                                                                                          ('早期感病', '表现为', '针叶变黄变红', '{"显著度": "高"}'),
                                                                                          ('中期感病', '表现为', '树脂分泌减少', '{"显著度": "高"}'),
                                                                                          ('中期感病', '表现为', '针叶变黄变红', '{"显著度": "高"}'),
                                                                                          ('中期感病', '表现为', '维管束堵塞', '{"显著度": "高"}'),
                                                                                          ('晚期感病', '表现为', '树脂分泌减少', '{"显著度": "高"}'),
                                                                                          ('晚期感病', '表现为', '针叶变黄变红', '{"显著度": "高"}'),
                                                                                          ('晚期感病', '表现为', '维管束堵塞', '{"显著度": "高"}'),
                                                                                          ('晚期感病', '表现为', '整株枯死', '{"显著度": "高"}');

-- === 16. 遥感技术关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('无人机高光谱', '搭载', '高光谱遥感', '{"分辨率": "高光谱"}'),
                                                                                          ('无人机高光谱', '搭载', '叶片光谱', '{"分辨率": "高光谱"}'),
                                                                                          ('无人机高光谱', '搭载', '冠层光谱', '{"分辨率": "高光谱"}'),
                                                                                          ('Sentinel-2卫星影像', '搭载', '高光谱遥感', '{"分辨率": "高光谱"}'),
                                                                                          ('Sentinel-2卫星影像', '搭载', '叶片光谱', '{"分辨率": "高光谱"}'),
                                                                                          ('Sentinel-2卫星影像', '搭载', '冠层光谱', '{"分辨率": "高光谱"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('高光谱遥感', '通过分析', '线性判别分析', '{"方法": "机器学习"}'),
                                                                                          ('高光谱遥感', '通过分析', '支持向量机', '{"方法": "机器学习"}'),
                                                                                          ('高光谱遥感', '通过分析', '随机森林', '{"方法": "机器学习"}'),
                                                                                          ('叶片光谱', '通过分析', '线性判别分析', '{"方法": "机器学习"}'),
                                                                                          ('叶片光谱', '通过分析', '支持向量机', '{"方法": "机器学习"}'),
                                                                                          ('叶片光谱', '通过分析', '随机森林', '{"方法": "机器学习"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('线性判别分析', '实现', '早期诊断', '{"精度": "高"}'),
                                                                                          ('支持向量机', '实现', '早期诊断', '{"精度": "高"}'),
                                                                                          ('随机森林', '实现', '早期诊断', '{"精度": "高"}');

-- === 17. 光谱特征关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('红边位置', '通过计算', '植被指数', '{"方法": "数学变换"}'),
                                                                                          ('红边位置', '通过计算', '诊断性光谱特征', '{"方法": "数学变换"}'),
                                                                                          ('蓝移', '通过计算', '植被指数', '{"方法": "数学变换"}'),
                                                                                          ('蓝移', '通过计算', '诊断性光谱特征', '{"方法": "数学变换"}'),
                                                                                          ('光谱特征', '通过计算', '植被指数', '{"方法": "数学变换"}'),
                                                                                          ('光谱特征', '通过计算', '诊断性光谱特征', '{"方法": "数学变换"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('红边波段', '产生', '光谱响应特征'),
                                                                       ('短波红外波段', '产生', '光谱响应特征'),
                                                                       ('蓝边拐点', '产生', '光谱响应特征'),
                                                                       ('植被指数', '增强', '诊断能力'),
                                                                       ('诊断性光谱特征', '增强', '诊断能力');

-- === 18. 生理参数变化关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('叶绿素含量下降', '导致', '叶片失水、萎缩、变黄变红', '{"机制": "生理功能障碍"}'),
                                                                                          ('叶绿素含量下降', '导致', '树脂分泌减少', '{"机制": "生理功能障碍"}'),
                                                                                          ('水分传输受阻', '导致', '叶片失水、萎缩、变黄变红', '{"机制": "生理功能障碍"}'),
                                                                                          ('水分传输受阻', '导致', '树脂分泌减少', '{"机制": "生理功能障碍"}'),
                                                                                          ('光合作用减弱', '导致', '叶片失水、萎缩、变黄变红', '{"机制": "生理功能障碍"}'),
                                                                                          ('光合作用减弱', '导致', '树脂分泌减少', '{"机制": "生理功能障碍"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('水分传输受阻', '影响', '叶绿素含量下降', '{"程度": "显著"}'),
                                                                                          ('叶绿素含量下降', '制约', '光合作用减弱', NULL);

-- === 19. 地区疫情监测关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('山东省威海市', '于时间监测', '疫情监测', '{"年份": "2019年"}'),
                                                                                          ('山东省威海市', '于时间监测', '疫情监测', '{"年份": "2020年"}'),
                                                                                          ('山东省威海市', '于时间监测', '疫情监测', '{"年份": "2021年"}'),
                                                                                          ('辽宁省抚顺市', '于时间监测', '疫情监测', '{"年份": "2019年"}'),
                                                                                          ('辽宁省抚顺市', '于时间监测', '疫情监测', '{"年份": "2020年"}'),
                                                                                          ('辽宁省抚顺市', '于时间监测', '疫情监测', '{"年份": "2021年"}'),
                                                                                          ('安徽省巢湖市', '于时间监测', '疫情监测', '{"年份": "2019年"}'),
                                                                                          ('安徽省巢湖市', '于时间监测', '疫情监测', '{"年份": "2020年"}'),
                                                                                          ('安徽省巢湖市', '于时间监测', '疫情监测', '{"年份": "2021年"}');

-- === 20. 多尺度监测体系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('叶片尺度', '构成', '多尺度监测', '{"层级": "空间尺度"}'),
                                                                                          ('单木尺度', '构成', '多尺度监测', '{"层级": "空间尺度"}'),
                                                                                          ('林分尺度', '构成', '多尺度监测', '{"层级": "空间尺度"}'),
                                                                                          ('多尺度监测', '实现', '早期诊断', '{"效果": "精准"}');

-- === 21. 防治措施与目标 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('检疫封锁', '针对', '松材线虫', '{"方式": "直接作用"}'),
                                                                                          ('检疫封锁', '针对', '松墨天牛', '{"方式": "直接作用"}'),
                                                                                          ('检疫封锁', '针对', '疫木', '{"方式": "直接作用"}'),
                                                                                          ('疫木清理', '针对', '松材线虫', '{"方式": "直接作用"}'),
                                                                                          ('疫木清理', '针对', '松墨天牛', '{"方式": "直接作用"}'),
                                                                                          ('疫木清理', '针对', '疫木', '{"方式": "直接作用"}'),
                                                                                          ('化学防治', '针对', '松材线虫', '{"方式": "直接作用"}'),
                                                                                          ('化学防治', '针对', '松墨天牛', '{"方式": "直接作用"}'),
                                                                                          ('化学防治', '针对', '疫木', '{"方式": "直接作用"}');

-- === 22. 生物防治体系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('生物防治', '利用', '花绒坚甲', '{"类型": "天敌昆虫"}'),
                                                                                          ('生物防治', '利用', '白僵菌', '{"类型": "天敌昆虫"}'),
                                                                                          ('花绒坚甲', '控制', '松墨天牛', '{"机制": "寄生或捕食"}'),
                                                                                          ('花绒坚甲', '控制', '松材线虫', '{"机制": "寄生或捕食"}'),
                                                                                          ('白僵菌', '控制', '松墨天牛', '{"机制": "寄生或捕食"}'),
                                                                                          ('白僵菌', '控制', '松材线虫', '{"机制": "寄生或捕食"}');

-- === 23. 算法与处理任务 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('竞争性自适应重加权算法', '应用于', '光谱降维', '{"领域": "特征选择"}'),
                                                                                          ('竞争性自适应重加权算法', '应用于', '波段优选', '{"领域": "特征选择"}'),
                                                                                          ('连续投影算法', '应用于', '光谱降维', '{"领域": "特征选择"}'),
                                                                                          ('连续投影算法', '应用于', '波段优选', '{"领域": "特征选择"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('光谱降维', '处理', '高光谱遥感'),
                                                                       ('光谱降维', '处理', '无人机高光谱'),
                                                                       ('波段优选', '处理', '高光谱遥感'),
                                                                       ('波段优选', '处理', '无人机高光谱');

-- === 24. 算法性能评估 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('光谱可分性', '决定', '识别精度', '{"影响程度": "关键"}'),
                                                                                          ('光谱可分性', '决定', '分类效果', '{"影响程度": "关键"}'),
                                                                                          ('诊断性波段', '决定', '识别精度', '{"影响程度": "关键"}'),
                                                                                          ('诊断性波段', '决定', '分类效果', '{"影响程度": "关键"}');

-- === 25. 经济损失链条 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('松材线虫病', '造成', '巨大经济损失', '{"程度": "严重"}'),
                                                                                          ('松材线虫病', '造成', '林产品损失', '{"程度": "严重"}'),
                                                                                          ('松材线虫病', '造成', '防治成本增加', '{"程度": "严重"}');

-- === 26. 生态服务功能影响 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('松材线虫病', '削弱', '松林保健效益', '{"方面": "生态服务"}'),
                                                                                          ('松材线虫病', '削弱', '疗养功能下降', '{"方面": "生态服务"}');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松林保健效益', '关联', '水土流失'),
                                                                       ('松林保健效益', '关联', '生态平衡破坏'),
                                                                       ('疗养功能下降', '关联', '水土流失'),
                                                                       ('疗养功能下降', '关联', '生态平衡破坏');

-- === 27. 气候因素影响 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('温度', '影响', '25℃最适线虫繁殖', '{"方式": "温度敏感"}'),
                                                                                          ('温度', '影响', '发病温度', '{"方式": "温度敏感"}'),
                                                                                          ('干旱', '影响', '25℃最适线虫繁殖', '{"方式": "温度敏感"}'),
                                                                                          ('干旱', '影响', '发病温度', '{"方式": "温度敏感"}'),
                                                                                          ('降水', '影响', '25℃最适线虫繁殖', '{"方式": "温度敏感"}'),
                                                                                          ('降水', '影响', '发病温度', '{"方式": "温度敏感"}');

-- === 28. 传播动力学 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('虫口密度', '决定', '传播概率', '{"关系": "正相关"}'),
                                                                                          ('传播概率', '需要', '治理阈值', '{"目的": "防控决策"}');

-- === 29. HOST_OF关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', 'HOST_OF', '油松'),
                                                                       ('松材线虫病', 'HOST_OF', '赤松'),
                                                                       ('松材线虫病', 'HOST_OF', '黑松'),
                                                                       ('松材线虫病', 'HOST_OF', '华山松'),
                                                                       ('松材线虫病', 'HOST_OF', '马尾松'),
                                                                       ('美国白蛾', 'HOST_OF', '麻栎'),
                                                                       ('美国白蛾', 'HOST_OF', '刺槐'),
                                                                       ('美国白蛾', 'HOST_OF', '元宝槭'),
                                                                       ('美国白蛾', 'HOST_OF', '法桐'),
                                                                       ('美国白蛾', 'HOST_OF', '桑树'),
                                                                       ('美国白蛾', 'HOST_OF', '臭椿'),
                                                                       ('美国白蛾', 'HOST_OF', '白蜡'),
                                                                       ('美国白蛾', 'HOST_OF', '核桃桃'),
                                                                       ('美国白蛾', 'HOST_OF', '板栗'),
                                                                       ('美国白蛾', 'HOST_OF', '樱桃'),
                                                                       ('美国白蛾', 'HOST_OF', '桃'),
                                                                       ('美国白蛾', 'HOST_OF', '柿'),
                                                                       ('美国白蛾', 'HOST_OF', '枣树'),
                                                                       ('美国白蛾', 'HOST_OF', '葡萄'),
                                                                       ('美国白蛾', 'HOST_OF', '杨属'),
                                                                       ('美国白蛾', 'HOST_OF', '柳树'),
                                                                       ('美国白蛾', 'HOST_OF', '连翘'),
                                                                       ('美国白蛾', 'HOST_OF', '紫丁香');

-- === 30. VECTOR_OF关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松褐天牛', 'VECTOR_OF', '松材线虫病'),
                                                                       ('褐幽天牛', 'VECTOR_OF', '松材线虫病');

-- === 31. USES_METHOD关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('风险评估', 'USES_METHOD', 'CLIMEX'),
                                                                       ('风险评估', 'USES_METHOD', '@risk'),
                                                                       ('风险评估', 'USES_METHOD', '生态位模型'),
                                                                       ('风险评估', 'USES_METHOD', '地理信息系统'),
                                                                       ('遥感监测', 'USES_METHOD', '高光谱遥感'),
                                                                       ('遥感监测', 'USES_METHOD', '无人机高光谱'),
                                                                       ('早期诊断', 'USES_METHOD', 'PCR检测');

-- === 32. OCCURS_IN关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', 'OCCURS_IN', '泰山'),
                                                                       ('松材线虫病', 'OCCURS_IN', '山东省'),
                                                                       ('松材线虫病', 'OCCURS_IN', '泰安市'),
                                                                       ('松材线虫病', 'OCCURS_IN', '天烛峰'),
                                                                       ('松材线虫病', 'OCCURS_IN', '桃花峪'),
                                                                       ('松材线虫病', 'OCCURS_IN', '玉泉寺'),
                                                                       ('美国白蛾', 'OCCURS_IN', '泰山'),
                                                                       ('美国白蛾', 'OCCURS_IN', '泰安市'),
                                                                       ('美国白蛾', 'OCCURS_IN', '山东省');

-- === 33. CONTROLLED_BY关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松褐天牛', 'CONTROLLED_BY', '引诱剂'),
                                                                       ('松褐天牛', 'CONTROLLED_BY', '假植木法'),
                                                                       ('松褐天牛', 'CONTROLLED_BY', '管氏肿腿蜂'),
                                                                       ('松褐天牛', 'CONTROLLED_BY', '花绒坚甲'),
                                                                       ('松褐天牛', 'CONTROLLED_BY', '白僵菌'),
                                                                       ('美国白蛾', 'CONTROLLED_BY', '飞机防治'),
                                                                       ('美国白蛾', 'CONTROLLED_BY', '无公害农药'),
                                                                       ('美国白蛾', 'CONTROLLED_BY', '频振式杀虫灯'),
                                                                       ('美国白蛾', 'CONTROLLED_BY', '自动虫情测报灯');

-- === 34. RESEARCHED_BY关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', 'RESEARCHED_BY', '申卫星'),
                                                                       ('美国白蛾', 'RESEARCHED_BY', '申卫星'),
                                                                       ('松材线虫病', 'RESEARCHED_BY', '山东农业大学'),
                                                                       ('美国白蛾', 'RESEARCHED_BY', '山东农业大学'),
                                                                       ('松材线虫病', 'RESEARCHED_BY', '植物保护学院');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('申卫星', 'AFFILIATED_WITH', '山东农业大学'),
                                                                       ('黄大卫', 'AFFILIATED_WITH', '山东农业大学');

-- === 35. IS_A关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', 'IS_A', '病害'),
                                                                       ('美国白蛾', 'IS_A', '害虫'),
                                                                       ('松褐天牛', 'IS_A', '天牛'),
                                                                       ('松褐天牛', 'IS_A', '媒介昆虫'),
                                                                       ('油松', 'IS_A', '松属'),
                                                                       ('赤松', 'IS_A', '松属');

-- === 36. AFFECTS关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', 'AFFECTS', '油松'),
                                                                       ('松材线虫病', 'AFFECTS', '古树名木'),
                                                                       ('松材线虫病', 'AFFECTS', '森林生态系统'),
                                                                       ('松材线虫病', 'AFFECTS', '生态安全'),
                                                                       ('松材线虫病', 'AFFECTS', '景观安全'),
                                                                       ('美国白蛾', 'AFFECTS', '阔叶树'),
                                                                       ('美国白蛾', 'AFFECTS', '果树林');

INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('泰山', 'HAS_RISK', '松材线虫病'),
                                                                       ('泰山', 'HAS_RISK', '美国白蛾');

-- === 37. MENTIONED_IN关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('泰山', 'MENTIONED_IN', '博士学位论文'),
                                                                       ('松材线虫病', 'STUDIED_IN', '博士学位论文'),
                                                                       ('美国白蛾', 'STUDIED_IN', '博士学位论文');

-- === 38. 学科发展阶段关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('萌芽期', 'NEXT_PERIOD', '形成期'),
                                                                       ('形成期', 'NEXT_PERIOD', '发展期'),
                                                                       ('发展期', 'NEXT_PERIOD', '完善期');

-- === 39. 人物与机构关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('曾凡勇', 'AFFILIATED_WITH', '中国林业科学研究院'),
                                                                       ('张星耀', 'AFFILIATED_WITH', '中国林业科学研究院'),
                                                                       ('萧刚柔', 'AFFILIATED_WITH', '中国林业科学研究院'),
                                                                       ('李寅恭', 'AFFILIATED_WITH', '国立中央大学'),
                                                                       ('戴芳澜', 'AFFILIATED_WITH', '中央农业实验所病虫害系'),
                                                                       ('邓叔群', 'AFFILIATED_WITH', '中央林业实验所');

-- === 40. 重要著作关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('萧刚柔', 'AUTHORED', '中国森林昆虫'),
                                                                       ('袁嗣令', 'AUTHORED', '中国乔灌木病害'),
                                                                       ('周尧', 'AUTHORED', '中国昆虫学史'),
                                                                       ('邓叔群', 'AUTHORED', '中国高等真菌');

-- === 41. 研究领域关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('萧刚柔', 'RESEARCHED_IN', '森林昆虫学'),
                                                                       ('李传道', 'RESEARCHED_IN', '森林病理学'),
                                                                       ('陈昌洁', 'RESEARCHED_IN', '松毛虫综合管理'),
                                                                       ('杨忠岐', 'RESEARCHED_IN', '生物防治');

-- === 42. 重要病虫害研究关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('萧刚柔', 'STUDIED', '松毛虫'),
                                                                       ('叶建仁', 'STUDIED', '松材线虫病'),
                                                                       ('杨忠岐', 'STUDIED', '美国白蛾'),
                                                                       ('骆有庆', 'STUDIED', '杨树天牛'),
                                                                       ('范国强', 'STUDIED', '泡桐丛枝病');

-- === 43. 防治技术关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('生物防治', 'USED_FOR', '美国白蛾'),
                                                                       ('白蛾周氏啮小蜂', 'CONTROLS', '美国白蛾'),
                                                                       ('花绒坚甲', 'CONTROLS', '天牛属昆虫'),
                                                                       ('白僵菌', 'CONTROLS', '松毛虫'),
                                                                       ('苏云金杆菌', 'CONTROLS', '松毛虫');

-- === 44. 机构发展关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('中央林业部林业科学研究所', 'EVOLVED_TO', '中国林业科学研究院'),
                                                                       ('江苏昆虫局', 'PIONEERED', '森林昆虫学'),
                                                                       ('上海商检局', 'PIONEERED', '植物检疫');

-- === 45. 学术组织关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('萧刚柔', 'LED', '中国林学会森林昆虫分会'),
                                                                       ('袁嗣令', 'LED', '中国林学会森林病理分会');

-- === 46. 实验室平台关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('森林保护学国家林业局重点实验室', 'AFFILIATED_WITH', '中国林业科学研究院'),
                                                                       ('森林保护学国家林业局重点实验室', 'AFFILIATED_WITH', '北京林业大学'),
                                                                       ('森林病虫害生物学国家林业局重点实验室', 'AFFILIATED_WITH', '东北林业大学'),
                                                                       ('昆嵛山森林生态系统定位研究站', 'AFFILIATED_WITH', '中国林业科学研究院');

-- === 47. 重大科技成果关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('中国森林昆虫', 'AWARDED', '国家科技进步二等奖'),
                                                                       ('美国白蛾生物防治技术研究', 'AWARDED', '国家科技进步二等奖'),
                                                                       ('松材线虫分子检测与媒介昆虫防治关键技术', 'AWARDED', '国家科技进步二等奖'),
                                                                       ('真菌杀虫剂产业化及森林害虫持续控制技术', 'AWARDED', '国家科技进步二等奖'),
                                                                       ('泡桐丛枝病发生机理及防治研究', 'AWARDED', '国家科技进步二等奖');

-- === 48. 教材专著关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('森林昆虫学', 'TEACHES', '森林保护学'),
                                                                       ('森林病理学', 'TEACHES', '森林保护学'),
                                                                       ('林木病理学', 'TEACHES', '森林病理学');

-- === 49. 研究方法关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('文献资料分析法', 'USED_IN', '学科发展历程'),
                                                                       ('专家访谈法', 'USED_IN', '学科发展历程'),
                                                                       ('综合分析法', 'USED_IN', '学科发展历程'),
                                                                       ('阶段分析法', 'USED_IN', '学科发展历程');

-- === 50. 时间事件关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('学科建立', 'OCCURRED_IN', '1958年'),
                                                                       ('恢复高考', 'OCCURRED_IN', '1977年'),
                                                                       ('改革开放', 'OCCURRED_IN', '1978年'),
                                                                       ('文化大革命', 'OCCURRED_IN', '1966年');

-- === 51. 地理分布关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', 'FOUND_IN', '江苏省'),
                                                                       ('美国白蛾', 'FOUND_IN', '辽宁省'),
                                                                       ('松毛虫', 'FOUND_IN', '湖南省'),
                                                                       ('杨树天牛', 'FOUND_IN', '宁夏');

-- === 52. 学科体系关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('森林昆虫学', 'PART_OF', '森林保护学'),
                                                                       ('森林病理学', 'PART_OF', '森林保护学'),
                                                                       ('林业植物检疫学', 'PART_OF', '森林保护学');

-- === 53. 人才培养关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('邓叔群', 'TAUGHT', '全国森林病理进修班'),
                                                                       ('普罗佐洛夫', 'TAUGHT', '全国森林昆虫教师进修班');

-- === 54. 国际合作关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('美国', 'COOPERATED_WITH', '森林保护学'),
                                                                       ('日本', 'COOPERATED_WITH', '森林保护学'),
                                                                       ('加拿大', 'COOPERATED_WITH', '森林保护学');

-- === 55. 法律法规关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('森林法', 'REGULATES', '森林保护学'),
                                                                       ('植物检疫条例', 'REGULATES', '林业植物检疫学'),
                                                                       ('森林病虫害防治条例', 'REGULATES', '森林保护学');

-- === 56. 防治理念演变关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('化学防治', 'EVOLVED_TO', '综合治理'),
                                                                       ('害虫综合防治', 'EVOLVED_TO', '害虫综合治理'),
                                                                       ('预防为主', 'LEADS_TO', '综合防治');

-- === 57. 学术会议关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('中国林学会森林病理分会', 'ORGANIZED', '全国森林病理学术讨论会'),
                                                                       ('中国林学会森林昆虫分会', 'ORGANIZED', '中国森林保护学术论坛'),
                                                                       ('中国林学会森林病理分会', 'ORGANIZED', '中国森林保护学术论坛');

-- === 58. 病害与病原关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
    ('松材线虫病', '由病原引起', '松材线虫');

-- === 59. 媒介昆虫传播关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
    ('松褐天牛', '是主要传播媒介', '松材线虫病');

-- === 60. 寄主植物关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('马尾松', '是主要寄主', '松材线虫病'),
                                                                       ('黑松', '是寄主', '松材线虫病'),
                                                                       ('赤松', '是寄主', '松材线虫病');

-- === 61. 天敌控制关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('花绒寄甲', '是天敌', '松褐天牛'),
                                                                       ('肿腿蜂', '是天敌', '松褐天牛'),
                                                                       ('管氏肿腿蜂', '是天敌', '松褐天牛'),
                                                                       ('莱氏猛叩甲', '是天敌', '松褐天牛'),
                                                                       ('松褐天牛卵金小蜂', '是天敌', '松褐天牛');

-- === 62. 地理分布关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('宁波', '有发生', '松材线虫病'),
                                                                       ('安徽', '有发生', '松材线虫病'),
                                                                       ('贵州', '有发生', '松材线虫病'),
                                                                       ('九华山', '有发生', '松材线虫病'),
                                                                       ('遵义', '有发生', '松材线虫病');

-- === 63. 研究方法与技术关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('生态位模型', '用于研究', '种群动态模型'),
                                                                       ('线性判别分析', '用于分析', '种群动态模型');

-- === 64. 作者与机构关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('展茂魁', '属于机构', '中国林业科学研究院'),
                                                                       ('杨忠岐', '属于机构', '中国林业科学研究院'),
                                                                       ('王小艺', '属于机构', '中国林业科学研究院'),
                                                                       ('来燕学', '属于机构', '中国林业科学研究院');

-- === 65. 时间关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('2012年', '是时间点', '调查开始'),
                                                                       ('2014年', '是时间点', '调查结束');

-- === 66. 蛀干害虫种类关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('短角椎天牛', '危害', '马尾松'),
                                                                       ('赤短梗天牛', '危害', '马尾松'),
                                                                       ('长角灰天牛', '危害', '马尾松'),
                                                                       ('小灰长角天牛', '危害', '马尾松'),
                                                                       ('松幽天牛', '危害', '马尾松'),
                                                                       ('日本脊吉丁', '危害', '马尾松'),
                                                                       ('松瘤象', '危害', '马尾松'),
                                                                       ('马尾松角胫象', '危害', '马尾松'),
                                                                       ('纵坑切梢小蠹', '危害', '马尾松'),
                                                                       ('横坑切梢小蠹', '危害', '马尾松'),
                                                                       ('哈氏松树皮象', '危害', '马尾松');

-- === 67. 防治措施关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('生物防治', '用于防治', '松褐天牛'),
                                                                       ('天敌释放', '是防治方法', '松褐天牛'),
                                                                       ('混交林', '可减轻', '松材线虫病');

-- === 68. 生态位关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松褐天牛', '有生态位重叠', '马尾松角胫象'),
                                                                       ('松褐天牛', '有生态位重叠', '小蠹虫');

-- === 69. 种群密度影响因素 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('林龄', '影响种群密度', '松褐天牛'),
                                                                       ('郁闭度', '影响种群密度', '松褐天牛'),
                                                                       ('树种丰富度指数', '影响种群密度', '松褐天牛'),
                                                                       ('日均相对湿度', '影响种群密度', '松褐天牛');

-- === 70. 学位关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('展茂魁', '撰写', '博士学位论文'),
                                                                       ('博士学位论文', '专业是', '森林保护学');

-- === 71. 新物种发现关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
    ('展茂魁', '发现新物种', '松脊吉丁肿腿蜂');

-- === 72. 评价体系创建关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
    ('杨忠岐', '创建评价体系', '忠岐指数');

-- === 73. 研究方法应用关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('生态位模型', '应用于研究', '松褐天牛'),
                                                                       ('回归模型', '用于预测种群密度', '松褐天牛');

-- === 74. 转主寄生关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('花绒寄甲', '可寄生', '短角椎天牛'),
                                                                       ('花绒寄甲', '可寄生', '松幽天牛'),
                                                                       ('花绒寄甲', '可寄生', '马尾松角胫象'),
                                                                       ('花绒寄甲', '可寄生', '松瘤象');

-- === 75. 防治效果关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('花绒寄甲', '寄生率可达', '松褐天牛'),
                                                                       ('松脊吉丁肿腿蜂', '单头可防治3到4头幼虫', '松褐天牛');

-- === 76. 传播能力关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
    ('松褐天牛', '单头可感染4株树', '松材线虫病');

-- === 77. 学位授予关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
    ('中国林业科学研究院', '授予博士学位', '展茂魁');

-- === 78. 松材线虫病与相关实体关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松材线虫病', '由何引起', '松材线虫'),
                                                                       ('松材线虫病', '危害', '松属植物'),
                                                                       ('松材线虫病', '危害', '马尾松'),
                                                                       ('松材线虫病', '危害', '黑松');

-- === 79. 媒介昆虫与松材线虫关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('松墨天牛', '携带', '松材线虫'),
                                                                       ('褐梗天牛', '携带', '松材线虫'),
                                                                       ('小灰长角天牛', '携带', '松材线虫'),
                                                                       ('西藏墨天牛', '携带', '松材线虫'),
                                                                       ('云杉花墨天牛', '携带', '松材线虫'),
                                                                       ('樟泥色天牛', '携带', '松材线虫'),
                                                                       ('粗鞘双条杉天牛', '携带', '松材线虫'),
                                                                       ('桃红颈天牛', '携带', '松材线虫');

-- === 80. 媒介昆虫传播机制 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('褐梗天牛', '通过什么传播', '松材线虫', '{"方式": "取食松针"}'),
                                                                                          ('褐梗天牛', '通过什么传播', '松材线虫', '{"方式": "产卵行为"}');

-- === 81. 地理分布关系（带比例） ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity, relation_property) VALUES
                                                                                          ('松墨天牛', '分布于', '黄山市', '{"比例": "85%"}'),
                                                                                          ('松墨天牛', '分布于', '邻水市', '{"比例": "82%"}'),
                                                                                          ('松墨天牛', '分布于', '仁怀市', '{"比例": "73%"}'),
                                                                                          ('松墨天牛', '分布于', '柞水县', '{"比例": "68%"}'),
                                                                                          ('松墨天牛', '分布于', '佛坪县', '{"比例": "95%"}'),
                                                                                          ('松墨天牛', '分布于', '青岛市', '{"比例": "25%"}'),
                                                                                          ('松墨天牛', '分布于', '大连市', '{"比例": "18%"}'),
                                                                                          ('褐梗天牛', '分布于', '青岛市', '{"比例": "72%"}'),
                                                                                          ('褐梗天牛', '分布于', '大连市', '{"比例": "65%"}'),
                                                                                          ('西藏墨天牛', '分布于', '柞水县', '{"比例": "25%"}');

-- === 82. 研究方法与技术应用 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('转录组测序', '使用技术', 'Illumina HiSeq'),
                                                                       ('实时荧光定量PCR', '使用技术', 'qRT-PCR'),
                                                                       ('RNA干扰', '使用技术', 'siRNA合成'),
                                                                       ('油红O染色', '用于研究', '脂肪代谢'),
                                                                       ('贝尔曼漏斗法', '用于分离', '松材线虫');

-- === 83. 分子机制与基因功能 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('Hccs', '参与', '氧化磷酸化'),
                                                                       ('Pcyt1', '参与', '脂肪代谢'),
                                                                       ('Ran基因', '参与', '核转运增强'),
                                                                       ('Hccs', '控制合成', '细胞色素c'),
                                                                       ('Pcyt1', '是', '磷脂酰胆碱胞苷酰转移酶基因');

-- === 84. 生理过程与机制 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('脂肪代谢', '提供', '能量代谢'),
                                                                       ('氧化磷酸化', '产生', '能量代谢'),
                                                                       ('运动性增强', '是什么的必要条件', '线虫脱离机制'),
                                                                       ('呼吸作用增强', '导致', '线虫脱离机制'),
                                                                       ('氧气浓度关键作用', '促进', '氧化磷酸化提升');

-- === 85. 生活史与行为特征 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('褐梗天牛', '具有特性', '直接交配产卵'),
                                                                       ('褐梗天牛', '具有特性', '针叶取食'),
                                                                       ('褐梗天牛', '具有特性', '特殊生活习性'),
                                                                       ('褐梗天牛', '具有', '口器结构'),
                                                                       ('褐梗天牛', '具有', '卵巢发育');

-- === 86. 时间与事件关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('博士学位论文', '完成于', '2020年'),
                                                                       ('首次发现', '发生于', '1982年');

-- === 87. 机构与作者关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('王洋', '属于', '南京林业大学'),
                                                                       ('陈凤毛', '属于', '南京林业大学'),
                                                                       ('陈凤毛', '担任', '导师');

-- === 88. 防治措施关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('诱捕器', '用于防治', '松墨天牛'),
                                                                       ('检疫检查站', '用于预防', '松材线虫病');

-- === 89. 传播途径关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('自然传播', '通过媒介', '松墨天牛'),
                                                                       ('人为传播', '通过方式', '运输疫木');

-- === 90. 新发现的关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('褐梗天牛', '是新传播媒介', '松材线虫病'),
                                                                       ('松针传播', '是新传播途径', '松材线虫病');

-- === 91. 代谢通路关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('脂肪酸β-氧化', '提供底物', '氧化磷酸化'),
                                                                       ('三羧酸循环', '提供底物', '氧化磷酸化');

-- === 92. 基因调控关系 ===
INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES
                                                                       ('Ran基因', '调控表达', 'Hccs'),
                                                                       ('Ran基因', '调控表达', 'Pcyt1');

CREATE TABLE IF NOT EXISTS graph_high_level_nodes (
                                                      id INT AUTO_INCREMENT PRIMARY KEY,
                                                      node_name VARCHAR(255) NOT NULL UNIQUE,
    node_type ENUM('core','generic') DEFAULT 'generic',
    description VARCHAR(512) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_node_name (node_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO graph_high_level_nodes (node_name, node_type, description) VALUES
                                                                           ('松材线虫病','core','核心病害概念'),
                                                                           ('松材线虫','core','主要病原线虫'),
                                                                           ('松墨天牛','core','重要媒介昆虫'),
                                                                           ('寄主','core','宿主整体概念'),
                                                                           ('媒介昆虫','core','媒介总体类别'),
                                                                           ('省份','generic','默认高级节点'),
                                                                           ('城市','generic','默认高级节点'),
                                                                           ('中国','generic','默认高级节点'),
                                                                           ('松属','generic','默认高级节点'),
                                                                           ('阔叶树','generic','默认高级节点'),
                                                                           ('天牛','generic','默认高级节点'),
                                                                           ('天敌昆虫','generic','默认高级节点'),
                                                                           ('线虫','generic','默认高级节点'),
                                                                           ('真菌','generic','默认高级节点'),
                                                                           ('算法','generic','默认高级节点'),
                                                                           ('遥感技术','generic','默认高级节点'),
                                                                           ('分子生物学技术','generic','默认高级节点'),
                                                                           ('年份','generic','默认高级节点'),
                                                                           ('病害','generic','默认高级节点'),
                                                                           ('农药药剂','generic','默认高级节点'),
                                                                           ('研究模型与软件','generic','默认高级节点'),
                                                                           ('基因','generic','默认高级节点'),
                                                                           ('代谢通路','generic','默认高级节点'),
                                                                           ('物理防治','generic','默认高级节点'),
                                                                           ('化学防治','generic','默认高级节点'),
                                                                           ('营林防治','generic','默认高级节点'),
                                                                           ('检疫措施','generic','默认高级节点'),
                                                                           ('生理指标','generic','默认高级节点'),
                                                                           ('风险评估','generic','默认高级节点'),
                                                                           ('早期诊断','generic','默认高级节点'),
                                                                           ('森林保护学','generic','默认高级节点'),
                                                                           ('森林昆虫学','generic','默认高级节点'),
                                                                           ('森林病理学','generic','默认高级节点'),
                                                                           ('林业植物检疫学','generic','默认高级节点'),
                                                                           ('博士学位论文','generic','默认高级节点'),
                                                                           ('国家科技进步二等奖','generic','默认高级节点'),
                                                                           ('生态服务','generic','默认高级节点'),
                                                                           ('多尺度监测','generic','默认高级节点'),
                                                                           ('能量代谢','generic','默认高级节点'),
                                                                           ('诊断','generic','默认高级节点'),
                                                                           ('天敌','generic','默认高级节点'),
                                                                           ('种群动态模型','generic','默认高级节点'),
                                                                           ('植被指数','generic','默认高级节点'),
                                                                           ('光谱特征','generic','默认高级节点');
