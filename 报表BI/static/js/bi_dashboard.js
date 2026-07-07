const api = (path) => fetch(path, { cache: "no-store" }).then((r) => {
  if (!r.ok) throw new Error(`${path} ${r.status}`);
  return r.json();
});
const $ = (id) => document.getElementById(id);
const fmt = (v) => Number(v || 0).toLocaleString("zh-CN");
const compact = (v) => {
  const n = Number(v || 0);
  if (Math.abs(n) >= 100000000) return `${(n / 100000000).toFixed(2)}亿`;
  if (Math.abs(n) >= 10000) return `${(n / 10000).toFixed(2)}万`;
  return fmt(n);
};
const charts = new Map();
function chart(id) {
  const node = $(id);
  if (!node) return null;
  const existed = charts.get(id);
  if (existed) return existed;
  const inst = echarts.init(node);
  charts.set(id, inst);
  return inst;
}
function dateLabel(key) {
  const s = String(key || "");
  return s.length === 8 ? `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}` : s;
}
function barOption(labels, values, color, unit) {
  return {
    color: [color],
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v) => `${fmt(v)}${unit}` },
    grid: { left: 110, right: 28, top: 10, bottom: 28 },
    xAxis: { type: "value", axisLabel: { color: "#5f7394", formatter: compact }, splitLine: { lineStyle: { color: "#e7f0fc", type: "dashed" } } },
    yAxis: { type: "category", inverse: true, data: labels, axisTick: { show: false }, axisLine: { show: false }, axisLabel: { color: "#20375d", fontWeight: 700, width: 100, overflow: "truncate" } },
    series: [{ type: "bar", data: values, barWidth: 12, itemStyle: { borderRadius: [0, 8, 8, 0], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: "#8dbbff" }, { offset: 1, color }]) }, label: { show: true, position: "right", color: "#1f355b", fontWeight: 800, formatter: ({ value }) => compact(value) } }]
  };
}
function truncateName(value, length = 8) {
  const text = String(value || "未知");
  return text.length > length ? `${text.slice(0, length)}...` : text;
}
function renderKpi(kpi) {
  const cards = [
    ["员", "会员总数", kpi.CustomerCount, "会员统计分析"],
    ["商", "商家总数", kpi.BusinessCount, "商家会员统计基础"],
    ["礼", "礼品 SKU", kpi.GiftCount, "礼品兑换统计基础"],
    ["单", "兑换订单", kpi.OrderCount, `订单积分流转 ${compact(kpi.CoinOut)}`]
  ];
  $("kpis").innerHTML = cards.map(([icon, label, value, note]) => `<article class="kpi"><div class="kpi-icon">${icon}</div><div><span>${label}</span><strong>${compact(value)}</strong><small>${note}</small></div></article>`).join("");
}
function renderTrend(rows) {
  const labels = rows.map((x) => dateLabel(x.DateKey));
  $("trendRange").textContent = labels.length ? `${labels[0]} 至 ${labels[labels.length - 1]}` : "暂无数据";
  chart("orderTrend")?.setOption({
    color: ["#176bf2", "#25bfd0"],
    tooltip: { trigger: "axis" },
    legend: { top: 4, textStyle: { color: "#5f7394" } },
    grid: { left: 56, right: 50, top: 42, bottom: 34 },
    xAxis: { type: "category", boundaryGap: false, data: labels, axisLabel: { color: "#5f7394" }, axisTick: { show: false }, axisLine: { lineStyle: { color: "#cddcf1" } } },
    yAxis: [{ type: "value", name: "订单数", axisLabel: { color: "#5f7394" }, splitLine: { lineStyle: { color: "#e7f0fc", type: "dashed" } } }, { type: "value", name: "积分", axisLabel: { color: "#5f7394", formatter: compact }, splitLine: { show: false } }],
    series: [{ name: "订单数", type: "line", smooth: true, symbolSize: 6, data: rows.map((x) => Number(x.OrderCount || 0)), areaStyle: { color: "rgba(23,107,242,.10)" }, lineStyle: { width: 3 } }, { name: "订单积分", type: "line", yAxisIndex: 1, smooth: true, symbolSize: 6, data: rows.map((x) => Number(x.TotalCoin || 0)), lineStyle: { width: 2, type: "dashed" } }]
  });
}
function renderStatus(rows) {
  const names = { 0: "无效", 1: "待使用", 2: "已使用" };
  const statusColors = { "待使用": "#89a4bd", "已使用": "#176bf2", "无效": "#ff5964" };
  const data = rows.map((x) => {
    const name = names[x.JFStatus] || `状态 ${x.JFStatus}`;
    return { name, value: Number(x.TotalCodes || 0), itemStyle: { color: statusColors[name] || "#25bfd0" } };
  });
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const used = data.find((item) => item.name === "已使用")?.value || 0;
  const rate = total ? `${(used / total * 100).toFixed(1)}%` : "0%";
  chart("jfStatus")?.setOption({
    tooltip: { trigger: "item", formatter: "{b}<br/>积分码：{c} 个<br/>占比：{d}%" },
    legend: { bottom: 8, icon: "roundRect", itemWidth: 14, itemHeight: 8, textStyle: { color: "#5f7394", fontWeight: 800 } },
    graphic: [
      { type: "circle", left: "center", top: "middle", shape: { r: 78 }, style: { fill: "rgba(23,107,242,.035)", stroke: "rgba(23,107,242,.18)", lineWidth: 2 } },
      { type: "text", left: "center", top: "39%", style: { text: rate, fill: "#176bf2", fontSize: 34, fontWeight: 950, align: "center" } },
      { type: "text", left: "center", top: "53%", style: { text: "积分码使用率", fill: "#60728f", fontSize: 12, fontWeight: 900, align: "center" } },
      { type: "text", left: "center", top: "61%", style: { text: `总量 ${fmt(total)}`, fill: "#102b5c", fontSize: 12, fontWeight: 900, align: "center" } }
    ],
    series: [
      { type: "pie", roseType: "area", minAngle: 8, radius: ["55%", "73%"], center: ["50%", "47%"], data, label: { formatter: "{b}\n{d}%", color: "#10213f", fontWeight: 900, lineHeight: 18 }, labelLine: { length: 14, length2: 10, lineStyle: { color: "#9db2c8" } }, itemStyle: { borderColor: "#fff", borderWidth: 4, shadowBlur: 18, shadowColor: "rgba(23,107,242,.18)" } },
      { type: "pie", radius: ["80%", "84%"], center: ["50%", "47%"], silent: true, label: { show: false }, data: [{ value: 1, itemStyle: { color: "rgba(23,107,242,.16)" } }] },
      { type: "pie", radius: ["43%", "45%"], center: ["50%", "47%"], silent: true, label: { show: false }, data: [{ value: 1, itemStyle: { color: "rgba(37,191,208,.16)" } }] }
    ]
  });
}
function renderProductTreemap(products) {
  chart("productTreemap")?.setOption({
    tooltip: { formatter: ({ name, value }) => `${name}<br/>积分贡献：${fmt(value)}` },
    series: [{
      type: "treemap",
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      top: 8,
      bottom: 14,
      left: 14,
      right: 14,
      label: { color: "#fff", fontWeight: 800, formatter: ({ name }) => truncateName(name, 9) },
      upperLabel: { show: false },
      itemStyle: { borderColor: "#fff", borderWidth: 3, gapWidth: 3 },
      levels: [{ color: ["#176bf2", "#25bfd0", "#10b981", "#d8a34c", "#5b8ff9"], colorSaturation: [0.38, 0.72] }],
      data: products.map((x) => ({ name: x.ProductName || "未知商品", value: Number(x.UsedCoin || 0) }))
    }]
  });
}
function renderBusinessPolar(businesses) {
  chart("businessPolar")?.setOption({
    color: ["#25bfd0"],
    tooltip: { trigger: "item", formatter: ({ name, value }) => `${name}<br/>商家会员：${fmt(value)}人` },
    angleAxis: { type: "value", axisLabel: { color: "#5f7394", formatter: compact }, splitLine: { lineStyle: { color: "#e7f0fc" } } },
    radiusAxis: { type: "category", data: businesses.map((x) => truncateName(x.BusinessCnName, 5)), axisLabel: { color: "#20375d", fontWeight: 800 }, axisLine: { show: false }, axisTick: { show: false } },
    polar: { center: ["50%", "52%"], radius: "72%" },
    series: [{ type: "bar", coordinateSystem: "polar", data: businesses.map((x) => Number(x.MemberCount || 0)), roundCap: true, barWidth: 9, itemStyle: { color: "#25bfd0" } }]
  });
}
function renderGiftBubble(gifts) {
  const rows = gifts.slice(0, 8).map((x) => {
    const count = Number(x.ExchangeCount || 0);
    const coin = Number(x.ExchangeCoin || 0);
    return {
      name: x.GiftName || "未知礼品",
      count,
      coin,
      avg: count ? Math.round(coin / count) : 0
    };
  });
  chart("giftBubble")?.setOption({
    color: ["#176bf2", "#25bfd0", "#d8a34c"],
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (items) => {
        const row = rows[items[0]?.dataIndex || 0] || {};
        return `${row.name}<br/>兑换次数：${fmt(row.count)} 次<br/>兑换积分：${fmt(row.coin)}<br/>客单积分：${fmt(row.avg)}`;
      }
    },
    legend: { top: 4, right: 8, icon: "roundRect", itemWidth: 14, itemHeight: 8, textStyle: { color: "#5f7394", fontWeight: 800 } },
    grid: { left: 54, right: 58, top: 48, bottom: 56 },
    xAxis: {
      type: "category",
      data: rows.map((x) => truncateName(x.name, 4)),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: "#cddcf1" } },
      axisLabel: { color: "#5f7394", fontWeight: 800, interval: 0, rotate: 22 }
    },
    yAxis: [
      { type: "value", name: "次数/积分", axisLabel: { color: "#5f7394", formatter: compact }, splitLine: { lineStyle: { color: "#e7f0fc", type: "dashed" } } },
      { type: "value", name: "客单积分", axisLabel: { color: "#5f7394", formatter: compact }, splitLine: { show: false } }
    ],
    series: [
      {
        name: "兑换次数",
        type: "bar",
        barMaxWidth: 18,
        data: rows.map((x) => x.count),
        itemStyle: { borderRadius: [8, 8, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "#176bf2" }, { offset: 1, color: "rgba(23,107,242,.45)" }]) }
      },
      {
        name: "兑换积分",
        type: "bar",
        barMaxWidth: 18,
        data: rows.map((x) => x.coin),
        itemStyle: { borderRadius: [8, 8, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "#25bfd0" }, { offset: 1, color: "rgba(37,191,208,.40)" }]) }
      },
      {
        name: "客单积分",
        type: "line",
        yAxisIndex: 1,
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        data: rows.map((x) => x.avg),
        lineStyle: { width: 3, color: "#d8a34c" },
        itemStyle: { color: "#d8a34c", borderColor: "#fff", borderWidth: 2 },
        areaStyle: { color: "rgba(216,163,76,.12)" }
      }
    ]
  });
}
const areaProvinceMap = {
  "金牛区": "四川", "蒲江县": "四川",
  "丰都县": "重庆", "沙坪坝区": "重庆",
  "罗湖区": "广东", "盐田区": "广东", "广州市": "广东", "萝岗区": "广东", "梦岗区": "广东",
  "浦东新区": "上海", "同安区": "福建"
};
const provinceMapName = { "广东": "广东省", "重庆": "重庆市", "四川": "四川省", "上海": "上海市", "福建": "福建省" };
function provinceOf(areaName) {
  const name = String(areaName || "");
  if (areaProvinceMap[name]) return areaProvinceMap[name];
  if (name.includes("重庆")) return "重庆";
  if (name.includes("上海")) return "上海";
  if (name.includes("广州") || name.includes("深圳") || name.includes("罗湖") || name.includes("盐田")) return "广东";
  if (name.includes("成都") || name.includes("金牛") || name.includes("蒲江")) return "四川";
  return "其他";
}
function aggregateProvince(areas) {
  const bucket = new Map();
  areas.forEach((area) => {
    const province = provinceOf(area.AreaName);
    const current = bucket.get(province) || { name: province, value: 0, orders: 0, coin: 0 };
    current.value += Number(area.MemberCount || 0);
    current.orders += Number(area.OrderCount || 0);
    current.coin += Number(area.OrderCoin || 0);
    bucket.set(province, current);
  });
  return [...bucket.values()].sort((a, b) => b.value - a.value);
}
function renderProvinceRank(provinces) {
  const node = $("provinceRank");
  if (!node) return;
  const max = Math.max(1, ...provinces.map((x) => x.value));
  node.innerHTML = provinces.slice(0, 7).map((item, index) => `
    <div class="province-row">
      <i>${index + 1}</i>
      <div><span>${item.name}</span><div class="province-bar"><b style="width:${Math.max(8, item.value / max * 100)}%"></b></div></div>
      <strong>${fmt(item.value)}</strong>
    </div>
  `).join("");
}
async function renderAreaMap(areas) {
  const provinces = aggregateProvince(areas);
  renderProvinceRank(provinces);
  const mapChart = chart("areaMap");
  if (!mapChart) return;
  const data = provinces.filter((x) => x.name !== "其他").map((x) => ({
    name: provinceMapName[x.name] || x.name,
    displayName: x.name,
    value: x.value,
    orders: x.orders,
    coin: x.coin
  }));
  try {
    const geo = await fetch("https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json", { cache: "force-cache" }).then((r) => r.json());
    echarts.registerMap("china-points-bi", geo);
    mapChart.setOption({
      tooltip: { trigger: "item", borderWidth: 0, backgroundColor: "rgba(10,30,68,.92)", textStyle: { color: "#fff", fontWeight: 800 }, formatter: ({ data: item, name }) => item ? `${item.displayName || name}<br/>会员数：${fmt(item.value)}<br/>订单数：${fmt(item.orders)}<br/>订单积分：${fmt(item.coin)}` : `${name}<br/>暂无业务数据` },
      visualMap: { min: 0, max: Math.max(1, ...data.map((x) => x.value)), left: 12, bottom: 8, itemWidth: 12, itemHeight: 94, text: ["高", "低"], inRange: { color: ["#e8f5ff", "#9ed0ff", "#4f91ff", "#176bf2", "#00c7d9"] }, textStyle: { color: "#60728f", fontWeight: 900 } },
      series: [{
        type: "map",
        map: "china-points-bi",
        roam: false,
        zoom: 1.28,
        center: [104, 35],
        data,
        label: { show: false },
        select: { disabled: true },
        itemStyle: { areaColor: "#dcecff", borderColor: "rgba(255,255,255,.95)", borderWidth: 1.1, shadowBlur: 14, shadowColor: "rgba(23,107,242,.20)" },
        emphasis: { label: { show: true, color: "#10213f", fontWeight: 950 }, itemStyle: { areaColor: "#17c3d5", shadowBlur: 22, shadowColor: "rgba(37,191,208,.35)" } }
      }]
    });
  } catch (_) {
    mapChart.setOption(barOption(provinces.map((x) => x.name), provinces.map((x) => x.value), "#176bf2", "人"));
  }
}
function renderAlerts(kpi, status, gifts, products, areas) {
  const totalCodes = status.reduce((s, x) => s + Number(x.TotalCodes || 0), 0);
  const used = status.find((x) => Number(x.JFStatus) === 2)?.TotalCodes || 0;
  const rate = totalCodes ? Number(used) / totalCodes * 100 : 0;
  const hotGift = gifts[0] || {};
  const hotProduct = products[0] || {};
  const hotArea = areas[0] || {};
  $("alerts").innerHTML = [
    ["danger", "!", "积分码使用率", `已使用 ${compact(used)} 个，占比 ${rate.toFixed(1)}%。`],
    ["warn", "礼", "热门礼品", `${hotGift.GiftName || "暂无"} 兑换 ${compact(hotGift.ExchangeCount)} 次。`],
    ["good", "商", "积分贡献商品", `${hotProduct.ProductName || "暂无"} 贡献 ${compact(hotProduct.UsedCoin)} 积分。`],
    ["info", "地", "地域热点", `${hotArea.AreaName || "暂无"} 会员 ${compact(hotArea.MemberCount)} 人。`]
  ].map(([cls, icon, title, text]) => `<article class="alert ${cls}"><i>${icon}</i><div><strong>${title}</strong><span>${text}</span></div></article>`).join("");
}
$("now").textContent = new Date().toLocaleString("zh-CN");
Promise.all([api("/api/bi/kpi"), api("/api/bi/order-trend"), api("/api/bi/gift-ranking"), api("/api/bi/business-member-ranking"), api("/api/bi/jfcode-status"), api("/api/bi/area-ranking"), api("/api/bi/product-coin-ranking")]).then(([kpi, orders, gifts, businesses, status, areas, products]) => {
  renderKpi(kpi || {});
  renderTrend(orders || []);
  renderStatus(status || []);
  renderProductTreemap(products || []);
  renderBusinessPolar(businesses || []);
  renderGiftBubble(gifts || []);
  renderAreaMap(areas || []);
  renderAlerts(kpi || {}, status || [], gifts || [], products || [], areas || []);
}).catch((error) => {
  $("alerts").innerHTML = `<article class="alert danger"><i>!</i><div><strong>数据加载失败</strong><span>${error.message}</span></div></article>`;
});
window.addEventListener("resize", () => charts.forEach((c) => c.resize()));
