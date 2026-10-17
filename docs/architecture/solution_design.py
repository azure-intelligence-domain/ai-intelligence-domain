"""Generate the solution design diagram as one self-contained SVG with official Azure icons.

Icons: Microsoft Azure Architecture Icons V24, embedded unmodified (Microsoft permits their use
in architecture diagrams and documentation). Usage: python solution_design.py <icons-dir> <out.svg>
"""

import base64
import html
import sys
from pathlib import Path

ICONS_DIR = Path(sys.argv[1])
OUT = Path(sys.argv[2])

ICONS = {
    "apim": "10042-icon-service-API-Management-Services.svg",
    "eventgrid": "10206-icon-service-Event-Grid-Topics.svg",
    "servicebus": "10836-icon-service-Azure-Service-Bus.svg",
    "appinsights": "00012-icon-service-Application-Insights.svg",
    "loganalytics": "00009-icon-service-Log-Analytics-Workspaces.svg",
    "functions": "10029-icon-service-Function-Apps.svg",
    "logicapps": "02631-icon-service-Logic-Apps.svg",
    "storage": "10086-icon-service-Storage-Accounts.svg",
    "identity": "10227-icon-service-Managed-Identities.svg",
    "cost": "00004-icon-service-Cost-Management-and-Billing.svg",
    "cosmos": "10121-icon-service-Azure-Cosmos-DB.svg",
    "subscription": "10002-icon-service-Subscriptions.svg",
    "eventhubs": "00039-icon-service-Event-Hubs.svg",
    "search": "10044-icon-service-Cognitive-Search.svg",
    "foundry": "035746832-icon-service-AI-Foundry.svg",
    "resourcegroup": "10007-icon-service-Resource-Groups.svg",
}


def icon_data(key: str) -> str:
    path = next(ICONS_DIR.rglob(ICONS[key]))
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode()


BLUE, INK, MUTED, LIVE, PLANNED, RED = "#0078D4", "#1B1B1F", "#5F6368", "#107C10", "#8A8886", "#A4262C"
out: list[str] = []
esc = html.escape


def text(x, y, s, size=13, weight=400, color=INK, anchor="start", italic=False):
    style = "font-style:italic;" if italic else ""
    out.append(
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
        f'text-anchor="{anchor}" style="{style}">{esc(s)}</text>'
    )


def box(x, y, w, h, label=None, *, fill="#FFFFFF", stroke="#C8C6C4", dashed=False, radius=10,
        label_color=MUTED, label_size=12, stroke_width=1.2, icon=None, badge=None, tag=None):
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    out.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}"{dash}/>'
    )
    tx = x + 12
    if icon:
        out.append(f'<image href="{icon_data(icon)}" x="{x + 10}" y="{y + 8}" width="18" height="18"/>')
        tx = x + 34
    if label:
        text(tx, y + 22, label, size=label_size, weight=600, color=label_color)
    if badge:
        status_badge(x + w - 12, y + 10, *badge)
    if tag:
        tag_chip(x + 12, y + h - 30, *tag)


def tag_chip(x, y, label, color):
    w = 12 + 6.2 * len(label)
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="4" fill="#FFFFFF" stroke="{color}"/>')
    text(x + w / 2, y + 14, label, size=10.5, weight=600, color=color, anchor="middle")


def status_badge(right_x, y, label, color):
    w = 8 + 7 * len(label)
    out.append(f'<rect x="{right_x - w}" y="{y}" width="{w}" height="18" rx="9" fill="{color}"/>')
    text(right_x - w / 2, y + 13, label, size=10, weight=700, color="#FFFFFF", anchor="middle")


def service(x, y, key, title, lines=(), *, dashed=False, w=200):
    """An Azure service: icon, name, detail lines."""
    box(x, y, w, 58 + 15 * len(lines), fill="#FFFFFF", stroke=PLANNED if dashed else "#C8C6C4",
        dashed=dashed, radius=8)
    out.append(f'<image href="{icon_data(key)}" x="{x + 10}" y="{y + 10}" width="38" height="38"/>')
    text(x + 56, y + 26, title, size=13, weight=600)
    for i, line in enumerate(lines):
        text(x + 56, y + 43 + 15 * i, line, size=11, color=MUTED)


def chip(x, y, label, *, dashed=False, w=None):
    w = w or 14 + 6.6 * len(label)
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    stroke = PLANNED if dashed else "#8A8886"
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="#F3F2F1" stroke="{stroke}"{dash}/>')
    text(x + w / 2, y + 15, label, size=11, color=INK if not dashed else MUTED, anchor="middle")
    return x + w + 6


def arrow(points, label=None, *, dashed=False, color=BLUE, label_at=None, label_anchor="middle"):
    d = "M " + " L ".join(f"{px} {py}" for px, py in points)
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    marker = "arrow-planned" if dashed else "arrow"
    out.append(
        f'<path d="{d}" fill="none" stroke="{PLANNED if dashed else color}" stroke-width="1.8"'
        f'{dash} marker-end="url(#{marker})"/>'
    )
    if label:
        lx, ly = label_at or points[len(points) // 2]
        width = 10 + 6.2 * len(label)
        bx = lx - width / 2 if label_anchor == "middle" else lx
        out.append(f'<rect x="{bx}" y="{ly - 12}" width="{width}" height="17" rx="4" fill="#FFFFFF" opacity="0.95"/>')
        text(bx + width / 2, ly + 1, label, size=11, color=PLANNED if dashed else BLUE, anchor="middle")


W, H = 1820, 1180

# --- Title and legend ----------------------------------------------------------------------
text(30, 46, "Azure Intelligence Domain — solution design", size=26, weight=700)
text(30, 72, "Integration platform (phase 1) and Intelligence domain (phase 2) · demo of the Nordic APIs Summit 2026 talk "
     "“AI as a new architectural domain”", size=13, color=MUTED)
lx = 1330
out.append(f'<rect x="{lx}" y="26" width="460" height="56" rx="8" fill="#FAF9F8" stroke="#E1DFDD"/>')
out.append(f'<rect x="{lx + 14}" y="38" width="34" height="14" rx="3" fill="#FFF" stroke="#C8C6C4"/>')
text(lx + 56, 50, "Live in Azure", size=11)
out.append(f'<rect x="{lx + 14}" y="60" width="34" height="14" rx="3" fill="#FFF" stroke="{PLANNED}" stroke-dasharray="4 3"/>')
text(lx + 56, 72, "Planned (step 8 / phase 2)", size=11)
out.append(f'<line x1="{lx + 230}" y1="45" x2="{lx + 266}" y2="45" stroke="{BLUE}" stroke-width="1.8" marker-end="url(#arrow)"/>')
text(lx + 274, 49, "Live flow", size=11)
out.append(f'<line x1="{lx + 230}" y1="67" x2="{lx + 266}" y2="67" stroke="{PLANNED}" stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#arrow-planned)"/>')
text(lx + 274, 71, "Planned flow", size=11)

# --- Consumers -------------------------------------------------------------------------------
box(30, 300, 200, 304, "Consumers · customer portal", fill="#FAF9F8", stroke="#E1DFDD")
cy = 340
for label, dashed in [("Webshop", False), ("Customer service", False), ("3PL partner", False),
                      ("Journey + smoke tests", False), ("AI agents", True)]:
    chip(46, cy, label, dashed=dashed, w=168)
    cy += 34
text(130, 532, "Staff: Google sign-in,", size=11, color=MUTED, anchor="middle")
text(130, 548, "thevaluehub.be only", size=11, color=MUTED, anchor="middle")
text(130, 572, "Every call carries", size=11, color=MUTED, anchor="middle")
text(130, 588, "Correlation-Id: ord-4711", size=11, weight=600, color=BLUE, anchor="middle")

# --- GitHub (delivery) -----------------------------------------------------------------------
box(260, 104, 1530, 128, "GitHub · azure-intelligence-domain organisation · one repository per ownership boundary",
    fill="#F6F8FA", stroke="#D0D7DE", label_color=INK, label_size=13)
x = 276
for repo, dashed in [("azure-landing-zone", False), ("integration-platform", False), ("contracts", False),
                     ("eventcatalog", False), ("ai-intelligence-domain", False), ("system-api-*", False),
                     ("process-api-*", False), ("*-intake", False), ("backend-systems", False), ("experience-api-*", False),
                     ("customer-portal", False), ("intelligence-domain", True)]:
    x = chip(x, 142, repo, dashed=dashed)
text(276, 194, "GitHub Actions per repository → reusable contract check (adidas API guidelines: lint, version, no breaking "
     "changes): no contract, no deploy → OIDC login, no stored secrets", size=12, color=MUTED)
text(276, 214, "Released contracts (asyncapi.yaml / openapi.yaml, topic eventcatalog) → EventCatalog, rebuilt daily, on GitHub Pages "
     "and Azure Storage · every deploy → deployment event in the tap", size=12, color=MUTED)

# --- Azure subscription ---------------------------------------------------------------------
box(260, 258, 1530, 900, "Azure subscription · pay-as-you-go · consumption tiers only · €10/month cap",
    fill="#FFFFFF", stroke=BLUE, stroke_width=1.6, label_color=BLUE, label_size=14, icon="subscription")

# France Central: API Management
box(280, 296, 300, 560, "France Central", fill="#F3F2F1", stroke="#E1DFDD")
box(292, 328, 276, 516, "rg-intplat-platform", fill="#EFF6FC", stroke="#A6CDEF", icon="resourcegroup",
    badge=("LIVE", LIVE), tag=("costguard=delete", RED))
service(304, 364, "apim", "Gateway for people", ["apim-intplat-demo · Consumption", "Correlation-Id · CORS",
                                                "staff: Google sign-in", "every call → tap, W3C trace"], w=252)
service(304, 494, "apim", "Gateway for agents", ["apim-intplat-agents · Consumption", "Entra token per agent",
                                                "every call → tap · 60/min", "MCP server behind it"], w=252)
text(304, 638, "APIs behind the gateways", size=11, weight=600, color=MUTED)
chip(304, 648, "Experience APIs · staff (Google)", w=250)
chip(304, 676, "Process + System APIs · internal", w=250)
chip(304, 704, "Event Intake API · Event Grid only", w=250)
chip(304, 732, "Agents: Order, Customer Service", w=250)
chip(304, 760, "[Platform] Health API (both)", w=220)
chip(304, 788, "MCP server · commands", dashed=True, w=190)

# Belgium Central
box(600, 296, 1170, 846, "Belgium Central", fill="#F3F2F1", stroke="#E1DFDD")

# API-led building blocks (planned)
box(612, 328, 820, 250, "API-led building blocks · one repository, resource group and identity each",
    fill="#EFF6FC", stroke="#A6CDEF", icon="resourcegroup", badge=("LIVE", LIVE),
    tag=("costguard=delete", RED))
service(628, 366, "functions", "Experience APIs", ["Webshop, Customer Service: Functions", "in France Central · Partner: gateway"], w=250)
service(628, 460, "functions", "Order Process API", ["Function · the brain", "state machine · policies"], w=250)
service(895, 460, "logicapps", "Intake flows", ["one Logic App per receiving", "domain: undo on OrderCancelled"], w=250)
service(895, 366, "functions", "System APIs", ["Functions (Flex Consumption)", "Salesforce · SAP · WMS · 3PL"], w=250)
service(1162, 366, "cosmos", "Source systems", ["Cosmos DB serverless,", "one per system, own naming"], w=255)
service(1162, 460, "functions", "3PL: strict partner API", ["booked, then picked up · 2.3", "only: the v2.4 mapping gets 400"], w=255)

# The customer portal (Belgium Central too, drawn under France Central for room)
box(280, 872, 300, 270, "Belgium Central · the front end", fill="#F3F2F1", stroke="#E1DFDD")
box(292, 904, 276, 226, "rg-intplat-customer-portal", fill="#EFF6FC", stroke="#A6CDEF", icon="resourcegroup",
    badge=("LIVE", LIVE), tag=("costguard=delete", RED))
service(304, 940, "storage", "Customer portal", ["Vue.js · Storage static website", "also on GitHub Pages",
                                                  "calls the gateway (CORS)"], w=252)

# Platform core (live)
box(612, 596, 820, 268, "rg-intplat-platform · integration-platform", fill="#EFF6FC", stroke="#A6CDEF",
    icon="resourcegroup", badge=("LIVE", LIVE), tag=("costguard=delete", RED))
service(628, 634, "eventgrid", "Event Grid topics", ["sales · finance · supply · logistics · order",
                                                   "+ platform · tap on every topic",
                                                   "push to consumers via the intake"], w=250)
service(628, 742, "servicebus", "Service Bus (Basic)", ["sbns-intplat-demo", "no queues: push wins (ADR 0016)"], w=250)
service(1110, 634, "appinsights", "Application Insights", ["appi-intplat-demo", "one trace per journey"], w=306)
service(1110, 734, "loganalytics", "Log Analytics", ["log-intplat-demo · 30 days", "daily cap 0.15 GB (free tier)"], w=306)

# Bottom row: catalog, identities, guardrails
box(612, 880, 265, 250, "rg-intplat-eventcatalog", fill="#EFF6FC", stroke="#A6CDEF", icon="resourcegroup",
    badge=("LIVE", LIVE), tag=("costguard=delete", RED))
service(624, 918, "storage", "EventCatalog", ["generated from released", "contracts · also on", "GitHub Pages"], w=241)
text(630, 1026, "Domains · services · events ·", size=11, color=MUTED)
text(630, 1042, "channels · owners · envelope", size=11, color=MUTED)

box(890, 880, 265, 250, "rg-intplat-identities", fill="#EFF6FC", stroke="#A6CDEF", icon="resourcegroup",
    badge=("LIVE", LIVE), tag=("never deleted", LIVE))
service(902, 918, "identity", "Managed identities", ["one per building block", "Contributor on its own", "resource group only"], w=241)
text(908, 1026, "GitHub OIDC: each repository", size=11, color=MUTED)
text(908, 1042, "deploys only its own group", size=11, color=MUTED)

box(1168, 880, 264, 250, "rg-intplat-guardrails", fill="#EFF6FC", stroke="#A6CDEF", icon="resourcegroup",
    badge=("LIVE", LIVE), tag=("never deleted", LIVE))
service(1180, 918, "cost", "Budget €10 / month", ["alerts 50 · 80 · 100 %"], w=240)
service(1180, 1002, "logicapps", "Kill switch", ["at 100 %: deletes costguard", "groups, purges API Mgmt"], w=240)

# Intelligence domain (phase 2)
box(1450, 328, 308, 528, "Intelligence domain · phase 2", fill="#FFFFFF", stroke=PLANNED, dashed=True,
    badge=("PHASE 2", PLANNED))
service(1464, 362, "eventhubs", "Ingest", ["drains the tap"], dashed=True, w=280)
service(1464, 457, "cosmos", "Remember · graph", ["order → flow → API → deploy"], dashed=True, w=280)
service(1464, 552, "search", "Remember · vectors", ["runbooks, incidents, contracts"], dashed=True, w=280)
service(1464, 647, "foundry", "Reason · Foundry", ["GraphRAG + LLM, with citations"], dashed=True, w=280)
service(1464, 742, "apim", "Expose · MCP + API", ["via the agent gateway"], dashed=True, w=280)

box(1450, 880, 308, 250, "rg-intplat-tap", fill="#EFF6FC", stroke="#A6CDEF", icon="resourcegroup",
    badge=("LIVE", LIVE), tag=("never deleted", LIVE))
service(1462, 918, "storage", "Tap · sttapintplatdemo", ["events queue, no expiry", "telemetry export (am-*)",
                                                        "dead letters of every consumer"], w=284)
text(1474, 1046, "Subscribe by default: created by", size=11, color=MUTED)
text(1474, 1062, "the platform, nobody can opt out", size=11, color=MUTED)

# --- Flows -----------------------------------------------------------------------------------
arrow([(230, 400), (304, 400)], "HTTPS", label_at=(267, 392))
arrow([(230, 520), (304, 520)], "token", dashed=True, label_at=(267, 512))
arrow([(556, 400), (628, 400)], "route", label_at=(592, 392))
arrow([(556, 540), (596, 540), (596, 515), (628, 515)])
text(590, 486, "commands", size=10, color=MUTED, anchor="end")
arrow([(878, 400), (895, 400)])
text(886, 361, "via gateway", size=10, color=MUTED, anchor="middle")
arrow([(1145, 400), (1162, 400)])
text(1153, 361, "managed identity", size=10, color=MUTED, anchor="middle")
arrow([(753, 454), (753, 460)])
arrow([(878, 490), (895, 490)])
arrow([(1020, 460), (1020, 454)])
arrow([(1145, 430), (1153, 430), (1153, 626), (820, 626), (820, 634)], "publish facts", label_at=(1075, 626))
arrow([(130, 604), (130, 1000), (304, 1000)], "staff", label_at=(130, 760))
arrow([(304, 1026), (271, 1026), (271, 450), (304, 450)])
arrow([(628, 680), (568, 680)], "push", label_at=(598, 672))
arrow([(580, 735), (610, 735), (610, 495), (628, 495)])
text(606, 610, "intake", size=10, color=MUTED, anchor="end")
arrow([(568, 712), (628, 712)], "actions", label_at=(598, 726))
arrow([(556, 460), (580, 460), (580, 587), (1263, 587), (1263, 634)], "one trace per call (W3C)", label_at=(1060, 587))
arrow([(1263, 701), (1263, 734)])
arrow([(1300, 991), (1300, 1002)])
arrow([(878, 720), (1090, 720), (1090, 870), (1441, 870), (1441, 940), (1462, 940)], "tap subscriptions",
      label_at=(1200, 870))
arrow([(1416, 790), (1436, 790), (1436, 990), (1462, 990)])
text(1426, 845, "export", size=10, color=BLUE, anchor="middle")
arrow([(1604, 880), (1604, 856)], dashed=True)
arrow([(1022, 232), (1022, 258)], "OIDC: each repository deploys its own resource group",
      label_at=(1180, 248))

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif">'
    '<defs>'
    f'<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>'
    f'<marker id="arrow-planned" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{PLANNED}"/></marker>'
    '</defs>'
    f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>'
    + "".join(out)
    + f'<text x="30" y="{H - 12}" font-size="10" fill="{MUTED}">Icons: Microsoft Azure Architecture Icons V24. '
    'Generated by docs/architecture/solution_design.py · regions verified 2026-10-16, step 7 2026-10-17.</text>'
    "</svg>"
)
OUT.write_text(svg, encoding="utf-8")
print(f"wrote {OUT} ({len(svg) // 1024} KB)")
