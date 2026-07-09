BEGIN TRANSACTION;

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '巴黎卢浮宫不要只盯着蒙娜丽莎', '巴黎', '第一次去卢浮宫才发现馆藏真的看不完。建议提前选好重点展厅，不要一进门就被人流带着走。除了蒙娜丽莎，胜利女神和拿破仑三世套房也非常震撼。晚上沿塞纳河散步，巴黎的浪漫会慢慢浮出来。', NULL, 32, datetime('now', '-6 days'), 2
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '巴黎卢浮宫不要只盯着蒙娜丽莎');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '东京浅草到上野适合第一次自由行', '东京', '浅草寺早上去人少很多，雷门拍照也不用挤。午后可以坐地铁到上野公园和阿美横町，吃饭购物都方便。东京交通看起来复杂，但用好换乘软件其实很顺。建议第一天不要排太多跨区景点。', NULL, 29, datetime('now', '-5 days'), 1
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '东京浅草到上野适合第一次自由行');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '伦敦博物馆爱好者会很幸福', '伦敦', '大英博物馆、国家美术馆、自然历史博物馆都很值得，但不要一天塞三个。很多博物馆免费，适合慢慢看。阴雨天也不影响行程。晚上去泰晤士河边走一走，大本钟和伦敦眼亮灯后很漂亮。', NULL, 21, datetime('now', '-5 days'), 3
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '伦敦博物馆爱好者会很幸福');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '罗马暴走两天脚真的会抗议', '罗马', '斗兽场、古罗马广场、万神殿、许愿池都很近，但石板路非常考验鞋子。建议早上去斗兽场，下午慢慢逛老城。冰淇淋店很多，随便走进一家都不太踩雷。不要带太大的包，安检和行走都麻烦。', NULL, 24, datetime('now', '-4 days'), 2
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '罗马暴走两天脚真的会抗议');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '纽约中央公园比想象中更适合发呆', '纽约', '纽约节奏很快，但中央公园让人突然慢下来。建议从大都会博物馆出来后沿着公园往南走，天气好时草坪上坐一会儿很舒服。时代广场可以体验一次，但不要把住宿安排在那里，夜里太吵。', NULL, 27, datetime('now', '-4 days'), 1
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '纽约中央公园比想象中更适合发呆');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '悉尼歌剧院日落时间最出片', '悉尼', '白天看歌剧院很标志，傍晚从皇家植物园方向看过去更温柔。海港大桥附近适合慢慢走，风很大记得带外套。邦迪海滩如果时间充裕可以安排半天，不一定下水，沿海步道就很好看。', NULL, 19, datetime('now', '-3 days'), 3
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '悉尼歌剧院日落时间最出片');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '新加坡亲子游很省心但天气太热', '新加坡', '地铁方便，城市干净，环球影城、滨海湾花园、夜间动物园都适合亲子。最大的挑战是热和湿，建议中午安排商场或酒店休息。小贩中心选择多，价格也比景区餐厅友好。', NULL, 23, datetime('now', '-2 days'), 2
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '新加坡亲子游很省心但天气太热');

INSERT INTO travel_app_guide (title, destination, content, image_url, likes, created_at, user_id)
SELECT '开普敦桌山一定要看天气再上', '开普敦', '桌山的云来得很快，缆车是否开放也受天气影响。建议把桌山安排成弹性行程，看到天气好就立刻去。海边公路风景很震撼，但自驾要注意安全，贵重物品不要放车里。', NULL, 18, datetime('now', '-1 days'), 1
WHERE NOT EXISTS (SELECT 1 FROM travel_app_guide WHERE title = '开普敦桌山一定要看天气再上');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '欧洲首次自由行路线：巴黎伦敦罗马怎么取舍', 'guide', '第一次去欧洲不建议贪多，选择两到三个核心城市更适合深度体验。', '第一次欧洲自由行常见误区是把太多城市塞进十天行程。巴黎适合艺术馆和城市漫步，伦敦适合博物馆和戏剧，罗马适合古迹和街巷。若假期只有七到十天，建议选择两座城市深度游，减少搬运行李和赶车时间。跨国交通可以提前关注火车和廉航，但要把机场交通和行李费用一起算进去。', 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=600&q=80', 980, datetime('now', '-5 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '欧洲首次自由行路线：巴黎伦敦罗马怎么取舍');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '日本樱花季订房提醒：热门城市价格明显上涨', 'news', '东京、京都、大阪樱花季房源紧张，建议提前确认可取消政策。', '随着樱花季临近，日本热门城市酒店搜索量持续上涨。东京上野、目黑川，京都清水寺、哲学之道，大阪城公园周边住宿价格波动明显。建议游客提前锁定可免费取消房源，并关注赏樱预测时间。若预算有限，可以选择交通便利的次热门区域住宿，用通勤时间换取更稳定的价格。', 'https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=600&q=80', 760, datetime('now', '-4 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '日本樱花季订房提醒：热门城市价格明显上涨');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '东南亚海岛雨季玩法调整建议', 'guide', '雨季不是不能去海岛，但行程需要更灵活，水上项目要看实时天气。', '东南亚部分海岛进入雨季后，天气变化较快。建议不要把浮潜、出海等项目安排得过满，至少留出一天机动时间。选择酒店时可以优先考虑有泳池、餐厅和室内活动空间的度假村。遇到短时强降雨不必焦虑，雨后天空和海面常常更清透，但风浪预警时一定不要勉强出海。', 'https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=600&q=80', 640, datetime('now', '-3 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '东南亚海岛雨季玩法调整建议');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '纽约热门景点预约制持续扩大', 'news', '部分博物馆与观景台建议提前预约，现场排队时间不确定。', '纽约多个热门景点在旅游旺季继续采用预约或分时入场机制。游客前往帝国大厦、洛克菲勒中心观景台、热门博物馆前，应提前查看官网时段。自由女神像和百老汇演出也建议提前规划。若临时出行，可以选择城市公园、街区漫步和免费展览作为替代。', 'https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?auto=format&fit=crop&w=600&q=80', 590, datetime('now', '-2 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '纽约热门景点预约制持续扩大');

INSERT INTO travel_app_travelnews (title, category, summary, content, cover_url, views_count, created_at)
SELECT '澳新自驾安全清单：左行规则和长距离补给', 'guide', '澳大利亚和新西兰自驾风景好，但驾驶规则、距离感和补给节奏需要提前适应。', '澳新自驾需要特别注意左侧通行和环岛让行规则。郊外路段距离长，部分地区手机信号弱，建议提前下载离线地图并规划加油点。新西兰山路和湖区道路景色迷人，但弯道较多，不要疲劳驾驶。澳大利亚部分地区夜间可能有野生动物穿行，建议尽量避免夜间长途开车。', 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=600&q=80', 820, datetime('now', '-1 days')
WHERE NOT EXISTS (SELECT 1 FROM travel_app_travelnews WHERE title = '澳新自驾安全清单：左行规则和长距离补给');

COMMIT;
