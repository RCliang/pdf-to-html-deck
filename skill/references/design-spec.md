# 设计规范 · 片段制作契约(作者:主代理与所有子代理必须遵守)

本规范与 `assets/shell.template.html` 的类名/CSS 一一对应。换主题时改 shell 的 tokens 与组件 CSS,**类名与结构不变**,本规范继续有效。

## 设计概念:夜航图(Night Chart)(可替换的主题示例)

「全书是一条学习航线」:深靛蓝夜航图底、航图网格、三色信标;每个「部分」是一段航线,每页底部有一条自绘航线(stroke 动画 + 节点依次点亮)。气质 = 严谨的工程手册 + 精美航海图。**克制**:动效只用在航线绘制与块级入场。

### 调色板(CSS 变量已在 shell 定义,片段内直接 `var()` 引用)

| 变量 | 值 | 用途 |
|---|---|---|
| `--paper` | #EAF0FA | 主文本 |
| `--muted` | #93A6C8 | 次文本/正文 |
| `--faint` | #5E739A | 弱化标注 |
| `--verm` | #FF5238 | 朱砂:关键词、强调数字、下划线 |
| `--amber` | #FFC24B | 航标金:节点、数字、徽标 |
| `--cyan` | #4EC9D4 | 信标青:图表线条、箭头、标签 |
| `--ink0` | #0A1424 | 最深底(代码块底) |
| `--ink1` | #0E1930 | 面板底 |
| `--ink2` | #14213B | 卡片底 |
| `--line` | rgba(150,180,255,.14) | 边框 |
| `--verm-bg` | rgba(255,82,56,.09) | 朱砂浅底(callout) |
| `--cyan-bg` | rgba(78,201,212,.08) | 青浅底 |

字体:展示标题 `--serif`(宋体系,自动应用于 `.k-h`/`.div-title`);正文 `--sans`(苹方/思源黑);标注/数字/代码 `--mono`(`.k-eyebrow .k-tag .k-num .k-code`)。

## 幻灯片骨架(严格照抄结构)

画布固定 1280×720,壳居中缩放。**内容必须放得下**:正文区高度约 400px(头部 ~190px + 航线 58px + 页脚 34px 之后)。

```html
<section class="slide" id="c21a" data-part="5" data-crumb="PART V · CH 16" data-title="RAG:架构与检索">
  <header class="s-head">
    <div class="k-eyebrow"><span class="tag">PART V · CH 16</span><span class="dim">书 p293-300</span><span class="tag c">RAG</span></div>
    <h2 class="k-h">检索增强生成 <em>RAG</em><span class="en">RETRIEVAL-AUGMENTED GENERATION</span></h2>
    <p class="k-lede">一段 1-2 句导语,概括本页要旨,≤ 90 字。</p>
  </header>
  <div class="s-body">
    <!-- 内容区,见组件词表 -->
  </div>
  <div class="route">…航线 SVG,见下…</div>
  <footer class="s-foot"><span>《书名》版本号</span><span class="dot">·</span><span>Part N</span><span class="pg">p123-130</span></footer>
</section>
```

规则:
- `<section>` 必须有唯一 `id`、`data-part`(部分号)、`data-crumb`(眉题短语)、`data-title`(目录短标题 ≤14 字)。
- **id 不得与壳内元素重名**(壳已用:`cover/toc/rail/hud/crumb/hint/stage/deck/wrap/zl/zr/btn-toc/btn-full` 及 `.close` 类所在容器)。实战翻过车:片段用 `id="toc"` 覆盖了目录浮层导致 JS 崩。
- 一页只讲一个主题;**宁可拆两页,不要塞爆**。
- 可引数据必须来自书文本,并标注书页码(pXXX);禁止 emoji/外部资源/`<style>`/`<script>`/lorem。

## 组件词表

```html
<div class="grid3"><!-- 或 grid2 grid4 -->
  <div class="k-card fu" style="--d:.05s">
    <div class="k-card-t">卡片标题</div>
    <div class="k-card-b">正文 ≤60 字,可含 <b class="hl">朱砂强调</b> 与 <span class="cy">青强调</span>。</div>
  </div>
</div>

<div class="k-num"><b>4-16</b><span>GRPO 组大小(经验值)</span></div>  <!-- 大数字;v/c 变体换色 -->

<ul class="k-flow"><li>编排</li><li>执行</li><li>聚合</li></ul>  <!-- 流程链,自动箭头 -->

<table class="k-table"><!-- 紧凑表;行多时加 class="k-table dense"(行距更紧) -->
  <thead><tr><th>方法</th><th>是否需要 critic</th></tr></thead>
  <tbody><tr><td>PPO</td><td>需要</td></tr></tbody>
</table>

<p class="k-quote">引用/金句<span class="k-cite">— 书 p136</span></p>
<div class="k-callout"><b>要点</b> 一句话关键提醒 ≤50 字。</div>  <!-- g 变体为青色「运行」横幅 -->
<div class="k-code"><pre>prompt = "..."</pre></div>

<div class="k-compare">
  <div class="k-col"><div class="k-card-t">在线</div><div class="k-card-b">…</div></div>
  <div class="vs">VS</div>
  <div class="k-col"><div class="k-card-t">离线</div><div class="k-card-b">…</div></div>
</div>

<span class="k-tag">RLHF</span> <span class="k-tag cy">TRL</span> <span class="k-tag am">2024</span> <span class="k-tag vm">CODE</span>

<div class="fig"><svg viewBox="0 0 860 400" role="img" aria-label="…">…</svg>
  <div class="figcap">图:标题与一句话解读</div></div>
```

布局:`.row`(横排)、`.col`(列内堆叠)、`.split-38/.split-62/.split-50/.split-58`(左窄右宽等两栏,flex:1)。
入场动画:主块加 `class="fu"` + `style="--d:.1s"`(0~.45s 交错);**不要**给所有小元素加。

## 签名元素:航线 band(每页必有)

```html
<div class="route"><svg viewBox="0 0 1160 80" preserveAspectRatio="xMidYMid meet">
  <path class="route-path" pathLength="1" d="M20,44 C160,12 300,72 440,44 S760,10 900,40 S1080,58 1140,44"/>
  <g class="rn" style="--d:.3s"><circle cx="150" cy="30" r="4.5"/><text x="118" y="16">节点名</text></g>
  <g class="rn" style="--d:.55s"><circle cx="330" cy="52" r="4.5"/><text x="298" y="72">节点名</text></g>
</svg></div>
```

- path 端点固定 `M20,44` 与 `x=1140`;节点圆心放路径上(目测即可,y∈[12,72])。
- **节点一律用 `<circle cx cy>` 定位,绝不用 `<g transform="…">` 定位**——壳的入场动画会覆盖 SVG transform 属性导致节点塌到原点(实战翻过车)。
- 每页 3-5 节点,标签 ≤6 字。

### SVG 图(.fig 内)规则

- viewBox 常用 `0 0 860 400` 或 `0 0 860 340/280/200`;线条 `stroke="var(--cyan)"` 宽 1.5-2;填充面 `var(--cyan-bg)`/`var(--verm-bg)`;
- 文本默认样式壳已给(13px paper 色):只写 `<text x y>内容</text>`;次要加 `class="mut"`,等宽加 `class="m"`;调大小写内联 `style="font-size:16px;font-weight:700"`;
- 强调节点:圆 `fill="var(--ink0)" stroke="var(--amber)"`,强调路径 `stroke="var(--verm)"`;
- 动效:`class="draw"`(描画)/`class="pop"`(浮现)/`class="seq"`(淡入)/`class="pulse"`(呼吸,最多 1 个/页);**动效元素 ≤6/页**;
- 结构类图优先(框+箭头+分区);不画 3D、渐变;marker/箭头 id 按文件加后缀避免全卷冲突(如 `arw21a`)。
- **标注不要压线条**:文字放空白带,曲线改道绕行;交点是用户第一眼会皱眉的地方。

## 代码讲解页(书中有真实代码示例时加)

骨架:section 加 `codeslide` 类(壳里有紧凑度量),两栏 `split-58`:

```html
<section class="slide codeslide" id="c22code" data-part="5" data-crumb="PART V · 代码 17" data-title="向量记忆实现">
  <!-- 头部同上;眉题首个 tag 用 <span class="tag am">CODE</span> + Listing 号/书页码 -->
  <div class="s-body">
    <div class="split-58">
      <div class="k-code tall fu" style="--d:.05s"><pre>…代码…</pre></div>
      <div class="col">
        <div class="k-card fu" style="--d:.15s"><div class="k-card-t"><span class="no">①</span>讲解标题</div>
          <div class="k-card-b">为什么这样写、对应书中哪个机制、坑。≤70 字。</div></div>
        <!-- 共 3-4 张,编号与代码内注释一一对应 -->
      </div>
    </div>
    <div class="k-callout g fu" style="--d:.42s"><b>运行</b>依赖 + 启动命令 + 预期输出一句话。</div>
  </div>
  <!-- route + footer 同上 -->
</section>
```

代码页硬约束(实战裁切教训):
1. 代码 **≤22 物理行、pre 内不留空行**(空行也占高,末行会被面板裁掉);
2. 代码忠实原书:允许重排缩进、用 `...` 注释删无关分支、加 ①②③ 注释;不允许改写逻辑或编造 API;
3. 高亮 span:`.k` 关键字/装饰器、`.s` 字符串、`.f` 函数名、`.c` 注释;
4. 讲解卡 ≤4 张、每张 ≤70 字;运行横幅单行 ≤80 字;
5. PDF 提取的代码缩进会被拍平——重排缩进时以语法层级为准,逐行核对括号闭合。

## 内容提炼准则

1. **忠实原文**:事实/数字/公式/术语中英对照来自章节文本;术语首现给英文。
2. **提炼为讲义,不是压缩原文**:每页回答「这章最重要的一件事」,配 2-4 个支撑点;数字优先(超参、复杂度、倍数);反直觉结论进 `.k-callout`。
3. **每页必有图或表**:`.fig` SVG / `.k-table` / `.k-flow` 至少其一;`.fig` 每页最多一张。

### 页面类型模板
- **概念页**:lede + 左 2-3 卡 + 右 `.fig` 结构图 + route
- **算法页**:lede + `.k-flow` 步骤链 + 公式卡(`.k-code` 或 SVG 文本)+ 超参 `.k-num` 行 + route
- **对比页**:lede + `.k-table`(≤5 行,dense ≤11 行)或 `.k-compare` + 选型 callout + route
- **代码页**:见上节
