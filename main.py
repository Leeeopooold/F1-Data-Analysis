import fastf1
import matplotlib.pyplot as plt

# 1. 开启缓存
# F1 的单场数据往往有几十MB，开启缓存后，只有第一次运行会下载，之后都是秒开。
# 在运行这段代码的同级目录下，新建一个空的文件夹叫 'f1_cache'
fastf1.Cache.enable_cache('f1_cache') 

# 2. 加载比赛
# 这里拿 2024巴林站（Bahrain）排位赛（'Q'）作为例子
session = fastf1.get_session(2024, 'Bahrain', 'Q')
session.load()

# 3. 提取车手数据
ver_lap = session.laps.pick_driver('VER').pick_fastest()
lec_lap = session.laps.pick_driver('LEC').pick_fastest()

# 4. 获取“遥测数据”（Telemetry）
ver_tel = ver_lap.get_telemetry()
lec_tel = lec_lap.get_telemetry()

# 5. 数据可视化
# 以赛道距离（Distance）为横坐标，速度（Speed）为纵坐标画一条线
plt.figure(figsize=(12, 6))

# 画维斯塔潘的线（使用红牛蓝）
plt.plot(ver_tel['Distance'], ver_tel['Speed'], label='VER', color='#0600EF', linewidth=2)

# 画勒克莱尔的线（使用法拉利红），稍微调高一点透明度防遮挡
plt.plot(lec_tel['Distance'], lec_tel['Speed'], label='LEC', color='#DC0000', linewidth=2, alpha=0.8)

# 图表装饰
plt.title("Verstappen vs Leclerc - 2024 Bahrain Q - Speed Comparison")
plt.xlabel("Distance on Track (m)")
plt.ylabel("Speed (km/h)")
plt.legend()
plt.grid()

# 如果想专门放大看发车大直道末端“一号弯”的拼刺刀重刹区
# 可以取消下面这行代码的注释，强行把X轴（赛道距离）限制在 400米 到 1200米 之间
# plt.xlim(400, 1200)

plt.show()