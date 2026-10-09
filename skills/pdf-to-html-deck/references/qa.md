# QA:渲染、审计与视觉验收

组装后必须逐页验证。两个层次:**DOM 精确审计**(快、可量化)+ **截图视觉验收**(慢、看观感)。

## 0. 本地渲染环境

```bash
cd <项目根> && python3 -m http.server 8123 &   # 壳 JS 需 http 上下文;file:// 下导航与截图不可靠
python3 scripts/build.py                        # 每次改片段后重建
```

浏览器用会话内建浏览器(node_repl bootstrap → `agent.browsers.getForUrl("http://127.0.0.1:8123/index.html")`),
视口 1440×860,舞台 1280×720 居中。单页直达:`http://127.0.0.1:8123/index.html?v=<随机>#/<页码>`——
**v 参数强制整页加载**,同文档 hash 跳转在渲染节流下不可靠。

## 1. 截图管线(带坑与解法)

**坑(全部实战踩过):**
- 面板被遮挡时渲染节流 → 截图冻结在过渡帧。**每次截前 `visibility.set(true)`**。
- 带裁剪区域(clip)的截图会产生 2×2 平铺错帧。**永远整视口截图**。
- 偶发截到透明/空帧(文件 ~6KB)。**以文件体积 >60KB 判有效**,无效则整页重载重截。
- 航线标签「首字符消失」多为合成器残影伪影:先用活 DOM `getExtentOfChar(0)` 验证,
  DOM 正常就不要"修"页面,强制重绘(`svg.style.transform='translateZ(0)'`)后重截。

**单页截图节奏(可靠配方):**
```
goto(…?v=NN#/页码) → waitForLoadState → 等 2.6-3s(动画完)
→ evaluate: 所有 svg 加 translateZ(0) 强制重绘
→ 等 1s → 试探性 screenshot 一次(丢弃) → 等 0.8s → 正式 screenshot
→ 写盘 work/render/pNN.png;体积 ≤60KB 视为空帧,重载重试(≤4 次)
```

## 2. DOM 精确审计(每页必做,几秒跑完)

在 `#/1` 页对全卷 evaluate,量化三类溢出:

```js
document.querySelectorAll('section.slide').forEach(s => {
  // a) 正文末元素超出 s-body 底
  // b) 代码页:pre.scrollHeight - pre.clientHeight > 2 → 末行被裁
  // c) 代码页:k-code 面板底 vs k-callout 顶 间距 < 2 → 横幅叠内容
});
```
指标说明:网格子元素溢出行框时 `getBoundingClientRect` 可能仍显示"在行内",
所以 b 用 scrollHeight(内容真实高度),c 用两个盒子真实边距。**审计为正=必改**,别信截图。

## 3. 视觉验收(visual-judge)

截图齐全后派 `documents:visual-judge` 子代理,**18 页/个**分批,输入:
- PNG 路径清单(说明"1440×860 视口、中间 1280×720 舞台");
- 每页主题一句话(验收员不懂书,给它对照物);
- 检查清单:溢出/裁切、叠压(尤其图内标注压线条、横幅压卡片)、SVG 文字截断、
  对比度、空洞/失衡、代码末行是否被切、讲解卡编号与代码序号是否对位;
- 输出格式:每页一行 JSON `{"page":N,"verdict":"pass|fail","issues":[…]}` + 总结行。

**验收员会误报**(如把动态对位读成错位):fail 项先亲自看图复核再改。
修复优先级:横幅叠内容 > 末行裁切 > 标注压线 > 留白失衡(最后者常可不修)。

## 4. 高频修复手法
- 代码末行被裁:删 pre 内空行/合并短行(保 ≤22 行);再不行删与讲解无关的代码分支(`...` 标注)。
- 横幅压卡片:卡片正文精简(≤70 字)或 section 加 `codeslide` 类(紧凑度量)。
- SVG 标注压线:文字移到空白带;曲线改道;标注并进标题行。
- 表格太高:`k-table` → `k-table dense`,或删 1-2 行次要行。
- 底部空:内容下补一个 `.fig` 总览图或把 callout 改通栏。
