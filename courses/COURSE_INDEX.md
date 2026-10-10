# 开关电源自学课程总目录（LTspice 驱动）

> **学习者画像**：GaN Power HEMT 器件/工艺开发工程师。电路起点为高中水平（KVL/KCL、欧姆定律、能量守恒），
> 半导体器件侧基础扎实。目标：从最基础的 RC/RL 一路学到市面成熟的 GaN 快充级电源电路。
>
> **方法**：每一课都是「物理直觉 → 数学推导 → LTspice 电路 → 真实仿真数据 → 手算对照 → 动手实验」。
> 每一课都带一个 **GaN 器件视角** 小节，把电路结论反推回你本职工作的器件指标。

---

## 每一课固定包含什么

| 文件 | 内容 |
|------|------|
| `README.md` | 本课导览：学习目标、前置课、时长、完成检查清单 |
| `讲义.md` | ① 物理直觉 ② 设计公式与计算要点 ③ **附录：完整数学推导** |
| `*.cir` | 可无头运行的 netlist，所有设计值都是 `.param`，方便你自己扫参数 |
| `*.asc` + `*.plt` | **全接线原理图**，在 LTspice 里双击打开、按 Run 就能跑，波形已预设 |
| `波形分析.md` | 每条波形逐点解读 + **手算 vs 仿真实测对照表**（含误差来源分析） |
| `练习.md` | 参数实验（先预测再仿真）+ 计算题，答案在文末 |
| `data/` | `.raw` / `.log` / 导出的 csv，所有分析数字都出自这里 |

## 怎么用

1. 你说「做 01-01」或「继续下一课」。
2. 我把那一课的全部交付物做出来并跑通仿真（`.log` 必须 0 error）。
3. 你在 LTspice 里打开 `.asc` 按 Run，对着 `讲义.md` 和 `波形分析.md` 学。
4. 做 `练习.md`，有问题随时问；我更新本文件的状态栏。

复现任意一课的仿真（在该课文件夹里执行）：
```bash
python ../../../tools/run_ltspice.py xxx.cir
python ../../../tools/ltspice_raw.py xxx.raw --stat "V(out)" "I(L1)"
```

---

## 进度总表

图例：⬜ 未开始　🟨 进行中　✅ 已完成

### 阶段 0 · 地基：从电路到波形到开关
| # | 课程 | 核心产出 | 状态 |
|---|------|---------|------|
| 00-01 | [LTspice 入门与 KVL/KCL 仿真验证](00-foundations/00-01-ltspice-intro/) | 会用 .op/.dc/.tran，跑通无头工作流 | ⬜ |
| 00-02 | [RC 充放电：时间常数与一阶微分方程](00-foundations/00-02-rc-transient/) | τ=RC 的推导与实测 | ⬜ |
| 00-03 | [RL 与电感：伏秒平衡雏形、续流路径](00-foundations/00-03-rl-inductor/) | **开关电源第一块地基** | ⬜ |
| 00-04 | [二极管整流与电容滤波：纹波公式](00-foundations/00-04-diode-rectifier/) | ΔV≈Io/(fC) 的来源 | ⬜ |
| 00-05 | [频域分析：滤波器、谐振与 Q 值](00-foundations/00-05-ac-frequency-response/) | 会读波特图，懂二阶欠阻尼 | ⬜ |
| 00-06 | [开关器件：理想开关→Si MOSFET→GaN HEMT](00-foundations/00-06-switching-devices/) | 后续所有课的开关模型库 | ⬜ |

### 阶段 1 · 非隔离 DC-DC（核心功底）
| # | 课程 | 核心产出 | 状态 |
|---|------|---------|------|
| 01-01 | [Buck 变换器 CCM 稳态](01-dcdc-nonisolated/01-01-buck-ccm/) | D=Vo/Vin、ΔIL、ΔVo 三大公式 | ⬜ |
| 01-02 | [Buck 的 DCM 与 CCM/DCM 边界](01-dcdc-nonisolated/01-02-buck-dcm/) | 临界电感 Lcrit | ⬜ |
| 01-03 | [Boost 升压变换器](01-dcdc-nonisolated/01-03-boost/) | M=1/(1-D)、RHP 零点直觉 | ⬜ |
| 01-04 | [Buck-Boost 与拓扑家族全景](01-dcdc-nonisolated/01-04-buck-boost/) | 三大基本拓扑统一视角 | ⬜ |
| 01-05 | [同步整流 Buck：死区、体二极管、反向导通](01-dcdc-nonisolated/01-05-sync-buck/) | 🔷 GaN 重点 | ⬜ |
| 01-06 | [损耗拆解与效率分析](01-dcdc-nonisolated/01-06-loss-efficiency/) | 五类损耗逐项量化 | ⬜ |
| 01-07 | [闭环控制入门：小信号模型与补偿](01-dcdc-nonisolated/01-07-closed-loop/) | 环路增益仿真、相位裕度 | ⬜ |

### 阶段 2 · 隔离拓扑
| # | 课程 | 核心产出 | 状态 |
|---|------|---------|------|
| 02-01 | [变压器与耦合电感建模](02-isolated/02-01-transformer-model/) | K 语句、漏感、同名端 | ⬜ |
| 02-02 | [反激 Flyback（DCM/CCM/RCD 钳位）](02-isolated/02-02-flyback/) | 最常见的小功率拓扑 | ⬜ |
| 02-03 | [正激 Forward 与磁复位](02-isolated/02-03-forward/) | 磁复位为什么必需 | ⬜ |
| 02-04 | [推挽 / 半桥 / 全桥 PWM](02-isolated/02-04-half-full-bridge/) | 双端拓扑与偏磁 | ⬜ |
| 02-05 | [移相全桥 PSFB 与 ZVS 初识](02-isolated/02-05-phase-shift-full-bridge/) | 第一次量化 ZVS | ⬜ |

### 阶段 3 · 软开关与谐振（GaN 主场）
| # | 课程 | 核心产出 | 状态 |
|---|------|---------|------|
| 03-01 | [软开关原理：ZVS/ZCS 的能量账](03-soft-switching/03-01-zvs-zcs-basics/) | 🔷 GaN 重点 | ⬜ |
| 03-02 | [LLC 谐振半桥（含现成样板剖析）](03-soft-switching/03-02-llc-resonant/) | 复用仓库已有 96W 样板 | ⬜ |
| 03-03 | [有源钳位反激 ACF](03-soft-switching/03-03-active-clamp-flyback/) | 🔷 GaN 快充主力拓扑 | ⬜ |
| 03-04 | [准谐振 QR / 临界导通 CRM](03-soft-switching/03-04-qr-crm/) | 谷底开关 | ⬜ |

### 阶段 4 · AC-DC 与成熟产品级电路
| # | 课程 | 核心产出 | 状态 |
|---|------|---------|------|
| 04-01 | [PFC 原理与 CCM Boost PFC](04-acdc-systems/04-01-boost-pfc-ccm/) | 双环控制、母线纹波 | ⬜ |
| 04-02 | [图腾柱无桥 PFC](04-acdc-systems/04-02-totem-pole-pfc/) | 🔷 GaN 零 Qrr 的杀手级应用 | ⬜ |
| 04-03 | [综合实战：65W GaN 快充（PFC+ACF/LLC）](04-acdc-systems/04-03-65w-gan-charger/) | 端到端整机设计 | ⬜ |
| 04-04 | [EMI、驱动与寄生参数](04-acdc-systems/04-04-emi-drive-parasitics/) | 从原理图走向真实板子 | ⬜ |

### 阶段 5 · 器件视角专题（结合本职工作）
| # | 课程 | 核心产出 | 状态 |
|---|------|---------|------|
| 05-01 | [GaN vs Si 同工况损耗对比仿真](05-device-topics/05-01-gan-vs-si-loss/) | 前置：01-06 | ⬜ |
| 05-02 | [Coss/Eoss 非线性与 Qrr 的电路后果](05-device-topics/05-02-coss-eoss-qrr/) | 器件参数 → 电路后果 | ⬜ |
| 05-03 | [共源电感、高 dv/dt 与栅极振铃](05-device-topics/05-03-lss-dvdt-ringing/) | 封装/版图寄生 | ⬜ |

---

## 学习笔记 / 已确认的关键结论

（每完成一课，我会在这里追加一行一句话的核心结论，形成你自己的速查表。）

| 课程 | 一句话结论 | 完成日期 |
|------|-----------|---------|
| — | — | — |
