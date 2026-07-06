const keywordGroups = {
  "바우처": ["홍보영상", "제품영상", "수출바우처", "혁신바우처", "마케팅 바우처", "콘텐츠 제작", "동영상 제작"],
  "홈쇼핑/인서트": ["홈쇼핑", "인서트", "상품소개영상", "TV홈쇼핑", "방송영상", "제품 시연영상"],
  "라이브커머스": ["라이브커머스", "모바일 라이브", "디지털커머스", "소담스퀘어", "온라인 판로", "쇼핑라이브"],
  "입찰": ["영상 제작 용역", "홍보물 제작", "콘텐츠 제작 용역", "촬영 편집", "SNS 영상"],
};

let activeFilter = "전체";
let notices = [];
let sources = [];
let updatedAt = "";

const noticeList = document.querySelector("#noticeList");
const noticeTemplate = document.querySelector("#noticeTemplate");
const searchInput = document.querySelector("#searchInput");
const refreshButton = document.querySelector("#refreshButton");
const tabs = document.querySelectorAll(".tab");

function classifyNotices(items) {
  return items.map((notice) => {
    const text = `${notice.title} ${notice.summary || ""}`;
    const matches = Object.entries(keywordGroups).map(([category, keywords]) => {
      const hitCount = keywords.filter((keyword) => text.includes(keyword)).length;
      return { category, hitCount };
    });
    const best = matches.sort((a, b) => b.hitCount - a.hitCount)[0];
    const score = Math.min(100, 55 + best.hitCount * 15);

    return {
      ...notice,
      category: best.hitCount > 0 ? best.category : "전체",
      score,
      summary:
        notice.summary ||
        `${notice.source}에서 확인할 후보 공고입니다. 제목 기준으로 ${best.category} 관련 키워드가 감지되었습니다.`,
    };
  });
}

function render() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = notices.filter((notice) => {
    const matchesTab = activeFilter === "전체" || notice.category === activeFilter;
    const matchesQuery = !query || `${notice.title} ${notice.summary} ${notice.source}`.toLowerCase().includes(query);
    return matchesTab && matchesQuery;
  });

  noticeList.innerHTML = "";

  if (filtered.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = notices.length === 0 ? "아직 감지된 공고가 없습니다. 수집을 먼저 실행해 주세요." : "조건에 맞는 공고가 없습니다.";
    noticeList.append(empty);
  } else {
    filtered.forEach((notice) => {
      const node = noticeTemplate.content.cloneNode(true);
      node.querySelector(".source").textContent = notice.source;
      node.querySelector("h2").textContent = notice.title;
      node.querySelector(".score").textContent = `관련도 ${notice.score}`;
      node.querySelector(".summary").textContent = notice.summary;
      node.querySelector(".category").textContent = notice.category;
      node.querySelector(".deadline").textContent = `${notice.deadline} · ${notice.detectedFrom || "키워드 감지"}`;
      node.querySelector(".notice-link").href = notice.url;
      noticeList.append(node);
    });
  }

  document.querySelector("#totalCount").textContent = notices.length;
  document.querySelector("#highCount").textContent = notices.filter((notice) => notice.score >= 80).length;
  document.querySelector("#sourceCount").textContent = sources.length;
  renderSourceStatus();
}

function renderSourceStatus() {
  const container = document.querySelector("#sourceStatusList");
  container.innerHTML = "";

  if (sources.length === 0) {
    const chip = document.createElement("span");
    chip.className = "source-chip";
    chip.textContent = "수집 결과 없음";
    container.append(chip);
    return;
  }

  sources.forEach((source) => {
    const chip = document.createElement("a");
    chip.className = `source-chip ${source.status === "error" ? "error" : ""} ${source.count > 0 ? "has-items" : ""}`;
    chip.href = source.url;
    chip.target = "_blank";
    chip.rel = "noreferrer";
    chip.textContent = source.status === "error" ? `${source.name} 오류` : `${source.name} ${source.count}건`;
    container.append(chip);
  });
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    activeFilter = tab.dataset.filter;
    render();
  });
});

searchInput.addEventListener("input", render);

refreshButton.addEventListener("click", () => {
  loadNotices();
});

async function loadNotices() {
  noticeList.innerHTML = '<p class="empty">수집 결과를 불러오는 중입니다.</p>';
  if (window.NOTICE_DATA) {
    const payload = window.NOTICE_DATA;
    notices = Array.isArray(payload.notices) ? payload.notices : [];
    sources = Array.isArray(payload.sources) ? payload.sources : [];
    updatedAt = payload.updatedAt || "";
    render();
    return;
  }
  try {
    const response = await fetch(`data/notices.json?time=${Date.now()}`);
    if (!response.ok) {
      throw new Error("notices.json 없음");
    }
    const payload = await response.json();
    notices = Array.isArray(payload.notices) ? payload.notices : [];
    sources = Array.isArray(payload.sources) ? payload.sources : [];
    updatedAt = payload.updatedAt || "";
  } catch (error) {
    notices = [];
    sources = [];
    updatedAt = "";
  }
  render();
}

loadNotices();
