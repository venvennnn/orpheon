const SELECTOR = "pre.mermaid, pre code.language-mermaid";

function collectNodes(): HTMLElement[] {
  const nodes: HTMLElement[] = [];
  document.querySelectorAll(SELECTOR).forEach((node) => {
    if (node instanceof HTMLElement) {
      if (node.matches("code.language-mermaid") && node.parentElement) {
        const pre = node.parentElement;
        if (!pre.dataset.mermaidSource) {
          pre.dataset.mermaidSource = node.textContent ?? "";
          pre.classList.add("mermaid");
          pre.textContent = pre.dataset.mermaidSource;
        }
        nodes.push(pre);
      } else {
        if (!node.dataset.mermaidSource) {
          node.dataset.mermaidSource = node.textContent ?? "";
        }
        nodes.push(node);
      }
    }
  });
  return nodes;
}

async function draw() {
  const nodes = collectNodes();
  if (!nodes.length) return;
  const mermaid = (await import("mermaid")).default;
  const dark = document.documentElement.classList.contains("dark");
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "strict",
    theme: dark ? "dark" : "neutral",
    fontFamily: "IBM Plex Sans, ui-sans-serif, sans-serif",
    flowchart: { curve: "basis", htmlLabels: false },
  });
  for (const node of nodes) {
    const source = node.dataset.mermaidSource ?? node.textContent ?? "";
    node.removeAttribute("data-processed");
    node.innerHTML = "";
    node.textContent = source;
  }
  await mermaid.run({ nodes });
}

export function initMermaid() {
  void draw();
  window.addEventListener("orpheon:theme", () => {
    void draw();
  });
}
