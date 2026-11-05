/* Shared management navigation. Existing page routes and public mounting helpers
   stay stable; theme.css and admin.css own the appearance. */
(function () {
  const NAV = [
    { href: "/admin", label: "后台首页", icon: "home" },
    { href: "/kb", label: "知识库录入", icon: "book" },
    { href: "/rag-eval", label: "RAG 评估", icon: "search" },
    { href: "/review", label: "飞轮待审", icon: "review" },
    { href: "/observability", label: "观测与成本", icon: "chart" },
    { href: "/topics", label: "主题分布", icon: "topics" },
    {
      href: "/acceptance", label: "分类器验收", icon: "check",
      children: [
        ["/acceptance", "总览"],
        ["/acceptance/eval", "评测详情"],
        ["/acceptance/data", "数据产物"],
        ["/acceptance/errors", "错例复核"],
      ],
    },
  ];
  const ICONS = {
    home: '<path d="m3 10 9-7 9 7v10H3V10Zm6 10v-7h6v7"/>',
    book: '<path d="M12 5v16M3 4h5a4 4 0 0 1 4 2 4 4 0 0 1 4-2h5v15h-5a4 4 0 0 0-4 2 4 4 0 0 0-4-2H3V4Z"/>',
    search: '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6M7 10h6m-3-3v6"/>',
    review: '<path d="M8 4h12v17H4V4h4m0-2h8v5H8V2Zm0 10 2 2 5-5m-7 9h8"/>',
    chart: '<path d="M4 3v17h17M8 15v-4m5 4V6m5 9V9"/>',
    topics: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    check: '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-6"/>',
    chat: '<path d="M20 11.5a8 8 0 0 1-8 8H4l1.5-4A8 8 0 1 1 20 11.5Z"/><path d="M8 10h8m-8 4h5"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    close: '<path d="m6 6 12 12M6 18 18 6"/>',
    spark: '<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z"/>',
  };
  function icon(name) {
    const template = document.createElement("template");
    template.innerHTML = '<svg class="mh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS[name] + '</svg>';
    return template.content.firstChild;
  }
  function link(href, label, on, cls) {
    const a = document.createElement("a");
    a.href = href;
    a.className = (on ? "on " : "") + (cls || "");
    a.textContent = label;
    if (on) a.setAttribute("aria-current", "page");
    return a;
  }
  function moduleOf(active) {
    return NAV.find((m) => m.href === active)
      || NAV.find((m) => m.href !== "/" && active.startsWith(m.href + "/"));
  }
  function iconButton(name, label, cls) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "mh-icon-button " + cls;
    b.setAttribute("aria-label", label);
    b.appendChild(icon(name));
    return b;
  }
  function renderAdminNav(active) {
    const aside = document.createElement("aside");
    aside.className = "mh-sidebar";
    aside.id = "mh-sidebar";
    aside.setAttribute("aria-label", "管理导航");
    const brand = document.createElement("a");
    brand.className = "mh-brand";
    brand.href = "/admin";
    brand.setAttribute("aria-label", "MewHelp 后台首页");
    brand.innerHTML = '<img src="/static/favicon.svg" alt="" /><span><strong>MewHelp<span>.</span></strong><small>让每一次沟通，都有回应</small></span>';
    aside.append(brand, iconButton("close", "关闭管理导航", "mh-close"));
    const caption = document.createElement("p");
    caption.className = "mh-nav-caption";
    caption.textContent = "工作空间 / WORKSPACE";
    const nav = document.createElement("nav");
    nav.className = "mh-nav";
    nav.setAttribute("aria-label", "后台模块");
    const mod = moduleOf(active);
    for (const m of NAV) {
      const a = link(m.href, m.label, m === mod);
      if (m === mod && m.href !== active) a.setAttribute("aria-current", "location");
      a.prepend(icon(m.icon));
      nav.appendChild(a);
    }
    const foot = document.createElement("div");
    foot.className = "mh-sidebar-foot";
    const chat = link("/", "返回聊天页面", false, "mh-chat-link");
    chat.prepend(icon("chat"));
    const version = document.createElement("div");
    version.className = "mh-version";
    version.innerHTML = '<span>Powered by MewHelp</span><span>v0.1</span>';
    foot.append(chat, version);
    aside.append(caption, nav, foot);
    return aside;
  }
  function mountAdminNav(active) {
    const existing = document.getElementById("mh-sidebar");
    if (existing) return existing;
    const body = document.body;
    const content = document.querySelector(".wrap");
    if (!content) return null;
    body.classList.add("mh-admin");
    content.id = "mh-content";
    content.setAttribute("role", "main");
    content.tabIndex = -1;
    const skip = link("#mh-content", "跳到页面内容", false, "mh-skip");
    const sidebar = renderAdminNav(active);
    const backdrop = document.createElement("button");
    backdrop.type = "button";
    backdrop.className = "mh-backdrop";
    backdrop.tabIndex = -1;
    backdrop.setAttribute("aria-label", "关闭管理导航");
    const header = document.createElement("header");
    header.className = "mh-shell-header";
    const menu = iconButton("menu", "打开管理导航", "mh-menu");
    menu.setAttribute("aria-controls", "mh-sidebar");
    menu.setAttribute("aria-expanded", "false");
    const breadcrumb = document.createElement("nav");
    breadcrumb.className = "mh-breadcrumb";
    breadcrumb.setAttribute("aria-label", "当前位置");
    breadcrumb.appendChild(link("/admin", "工作空间", false));
    const separator = document.createElement("span");
    separator.className = "mh-separator";
    separator.textContent = "/";
    separator.setAttribute("aria-hidden", "true");
    const current = document.createElement("span");
    current.className = "mh-current";
    current.textContent = moduleOf(active)?.label || "后台管理";
    breadcrumb.append(separator, current);
    const label = document.createElement("span");
    label.className = "mh-workspace-label";
    label.append(icon("spark"), document.createTextNode("管理工作台"));
    header.append(menu, breadcrumb, label);
    body.prepend(skip, sidebar, backdrop, header);

    // Move the existing nodes, preserving page IDs and attached event handlers.
    const bar = content.querySelector(".topbar");
    if (bar) {
      const heading = document.createElement("div");
      heading.className = "mh-page-heading";
      for (const node of [...bar.children]) {
        if (node.matches("h1, .sub")) heading.appendChild(node);
        else if (node.matches(".spacer")) node.remove();
      }
      bar.prepend(heading);
      const mod = moduleOf(active);
      if (mod?.children) {
        const sub = document.createElement("nav");
        sub.className = "mh-subnav";
        sub.setAttribute("aria-label", "分类器验收页面");
        for (const [href, text] of mod.children) sub.appendChild(link(href, text, href === active));
        bar.after(sub);
      }
    }
    const mobile = window.matchMedia("(max-width: 900px)");
    function setOpen(open, restoreFocus = true) {
      open = open && mobile.matches;
      body.classList.toggle("mh-nav-open", open);
      menu.setAttribute("aria-expanded", String(open));
      content.inert = open;
      header.inert = open;
      sidebar.inert = mobile.matches && !open;
      if (open) sidebar.querySelector(".mh-close").focus();
      else if (restoreFocus && mobile.matches) menu.focus();
    }
    menu.addEventListener("click", () => setOpen(true));
    sidebar.querySelector(".mh-close").addEventListener("click", () => setOpen(false));
    backdrop.addEventListener("click", () => setOpen(false));
    mobile.addEventListener("change", () => setOpen(false, false));
    sidebar.addEventListener("keydown", (e) => {
      if (!body.classList.contains("mh-nav-open")) return;
      if (e.key === "Escape") { e.preventDefault(); setOpen(false); }
      if (e.key !== "Tab") return;
      const focusable = [...sidebar.querySelectorAll("a, button")].filter((el) => el.getClientRects().length);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    setOpen(false, false);
    return sidebar;
  }
  window.renderAdminNav = renderAdminNav;
  window.mountAdminNav = mountAdminNav;
})();
