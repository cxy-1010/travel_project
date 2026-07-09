BEGIN TRANSACTION;

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '第一次去青岛的海边散步体验', '青岛', '傍晚从栈桥一路走到八大关，海风很舒服，路边的老建筑也很适合慢慢拍照。建议不要把行程排太满，青岛更适合留出半天发呆，看海、喝咖啡、吃一顿海鲜小馆子。', NULL, 18, datetime('now', '-16 days'), 2
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '第一次去青岛的海边散步体验');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '杭州西湖雨天反而更有味道', '杭州', '原本担心下雨会影响游玩，结果烟雨里的西湖特别安静。推荐从断桥走到曲院风荷，带一把轻便雨伞就好。傍晚去湖滨银泰附近吃饭，交通方便，也不会太折腾。', NULL, 26, datetime('now', '-15 days'), 1
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '杭州西湖雨天反而更有味道');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '重庆三天两晚真的要少爬坡', '重庆', '重庆的路比想象中更立体，导航显示几百米也可能走到怀疑人生。解放碑、洪崖洞、山城步道可以放在一天，但一定穿舒服的鞋。火锅推荐早点去，晚上热门店排队很久。', NULL, 31, datetime('now', '-14 days'), 3
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '重庆三天两晚真的要少爬坡');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '厦门鼓浪屿别只打卡网红墙', '厦门', '鼓浪屿真正舒服的地方在小巷子里。早上第一班船上岛，人少很多，可以慢慢逛老别墅和海边小路。岛上吃饭略贵，建议带点水和小零食，下午再回市区吃沙茶面。', NULL, 22, datetime('now', '-13 days'), 2
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '厦门鼓浪屿别只打卡网红墙');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '苏州园林适合慢下来听风', '苏州', '拙政园很漂亮，但人也多。更喜欢艺圃和网师园，空间不大却很精致。建议上午园林，下午平江路，晚上坐船看灯。不要赶景点数量，苏州的美在细节里。', NULL, 17, datetime('now', '-12 days'), 1
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '苏州园林适合慢下来听风');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '长沙周末吃喝很快乐但要错峰', '长沙', '五一广场附近吃的很多，但排队也很夸张。建议上午去橘子洲，下午去湖南博物院，晚上再吃小龙虾和臭豆腐。茶颜悦色可以选非核心商圈门店，排队时间短很多。', NULL, 28, datetime('now', '-11 days'), 3
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '长沙周末吃喝很快乐但要错峰');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '南京梧桐大道适合秋天再来一次', '南京', '这次去南京最喜欢陵园路的梧桐和明孝陵。中山陵台阶不少，体力一般的话别和太多景点塞在同一天。晚上去秦淮河看看灯就好，夫子庙商业气息比较重。', NULL, 20, datetime('now', '-10 days'), 2
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '南京梧桐大道适合秋天再来一次');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '广州早茶让我愿意早起', '广州', '广州的早茶真的值得专门安排一顿。点心分量不小，建议多人一起去可以多尝几样。沙面适合饭后散步，永庆坊也挺好逛。夏天比较闷热，行程要留室内休息时间。', NULL, 24, datetime('now', '-9 days'), 1
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '广州早茶让我愿意早起');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '昆明是很适合中转放松的城市', '昆明', '原本只把昆明当云南中转，结果住了两天很舒服。翠湖公园、云南大学、斗南花市都不累，天气也温和。建议把昆明当作进入云南前的缓冲站，节奏会舒服很多。', NULL, 16, datetime('now', '-8 days'), 3
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '昆明是很适合中转放松的城市');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '哈尔滨冬天好看但保暖要认真', '哈尔滨', '冰雪大世界非常震撼，但手机和人都会被冻到没电。帽子、围巾、手套、暖宝宝一个都不能少。中央大街适合傍晚去，灯光亮起来后氛围更好，马迭尔冰棍可以体验但别逞强。', NULL, 35, datetime('now', '-7 days'), 2
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '哈尔滨冬天好看但保暖要认真');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '云南小众古镇路线：避开人流的4天慢旅行', 'guide', '从建水到巍山，一条更安静的云南古镇路线，适合喜欢慢节奏和人文街巷的旅行者。', '这条路线不追求打卡数量，而是把时间留给街巷、老建筑和当地小吃。第一天抵达建水，逛朱家花园和临安古城，晚上吃烧豆腐。第二天坐小火车看田野和古桥。第三天前往巍山，感受更生活化的古城节奏。第四天留给咖啡馆、菜市场和返程。建议选择轻便行李，古城石板路拖箱不太方便。', 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=80', 860, datetime('now', '-6 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '云南小众古镇路线：避开人流的4天慢旅行');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '海岛旅行防晒与防蚊清单更新', 'news', '多地进入海岛旅行旺季，防晒、防蚊和补水成为近期游客反馈最多的问题。', '近期海岛目的地热度上升，游客在户外停留时间明显增加。建议准备高倍防晒霜、遮阳帽、防晒衣、驱蚊液和补水电解质饮品。浮潜、赶海等活动前应确认天气和潮汐信息，避免在风浪较大时下水。若出现晒伤，应及时转移到阴凉处，并进行冷敷和补水。', 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80', 430, datetime('now', '-5 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '海岛旅行防晒与防蚊清单更新');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '西北环线7日自驾补给点建议', 'guide', '青甘大环线距离长、温差大，合理安排补给点比赶路更重要。', '西北环线适合提前规划每日车程。西宁出发后，建议在青海湖、茶卡、德令哈、敦煌、张掖等节点补给油、水和食物。高原和戈壁地区昼夜温差大，车上应准备厚外套和基础药品。部分路段信号不稳定，离线地图和纸质路线备份很有必要。不要疲劳驾驶，景色再美也要把安全放在第一位。', 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=600&q=80', 1120, datetime('now', '-4 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '西北环线7日自驾补给点建议');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '暑期亲子游订房提醒：优先确认早餐与交通', 'news', '亲子游订单增加，酒店早餐、接驳和房型细节成为影响体验的关键因素。', '暑期亲子游中，酒店位置和服务细节会显著影响体验。订房前建议确认儿童早餐政策、加床费用、地铁或景区接驳、洗衣设施以及周边餐饮。热门亲子酒店房源紧张，尽量提前预订并保留可取消选项。带低龄儿童出行时，建议每天只安排一到两个核心项目，避免全家都被行程拖累。', 'https://images.unsplash.com/photo-1504150558240-0b4fd8946624?auto=format&fit=crop&w=600&q=80', 690, datetime('now', '-3 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '暑期亲子游订房提醒：优先确认早餐与交通');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '城市漫步路线：上海梧桐区半日计划', 'guide', '从武康路到衡山路，一条适合拍照、咖啡和建筑爱好者的上海半日路线。', '这条路线建议从武康大楼开始，沿武康路慢慢走到安福路，再转向衡山路。沿途有不少老洋房、独立书店和咖啡店。拍照时注意不要影响居民生活，很多建筑仍是日常居住空间。午后阳光透过梧桐树的时间最适合散步，傍晚可以去徐家汇或淮海中路吃饭。', 'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?auto=format&fit=crop&w=600&q=80', 770, datetime('now', '-2 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '城市漫步路线：上海梧桐区半日计划');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '高铁周边短途游热度上升', 'news', '周末两日游更偏向高铁直达城市，轻行李、少换乘成为新趋势。', '近期平台数据显示，高铁两小时圈内的短途游关注度上升。游客更倾向选择无需复杂换乘的城市，周五晚出发、周日晚返程成为常见安排。建议优先选择车站到酒店交通便利的区域，并提前确认返程高峰票源。短途游不必追求景点数量，选择一两个核心体验更能提升放松感。', 'https://images.unsplash.com/photo-1474487548417-781cb71495f3?auto=format&fit=crop&w=600&q=80', 540, datetime('now', '-1 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '高铁周边短途游热度上升');

COMMIT;
