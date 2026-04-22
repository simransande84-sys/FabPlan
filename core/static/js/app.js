// core/static/js/app.js

function openTab(evt, tabName) {
    // Get all elements with class="tab-content" and hide them
    const tabcontent = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
        tabcontent[i].classList.remove("active");
    }

    // Get all elements with class="tab-btn" and remove the class "active"
    const tablinks = document.getElementsByClassName("tab-btn");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    const selectedTab = document.getElementById(tabName);
    selectedTab.style.display = "block";
    
    // Slight delay to allow display:block to apply before adding class for animation
    setTimeout(() => {
        selectedTab.classList.add("active");
    }, 10);
    
    evt.currentTarget.classList.add("active");
}

// Drawer Management
let currentOrderId = null;

function openDrawerTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("d-tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
        tabcontent[i].classList.remove("active");
    }

    const tablinks = document.getElementsByClassName("d-tab-btn");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }

    document.getElementById(tabName).style.display = "block";
    setTimeout(() => { document.getElementById(tabName).classList.add("active"); }, 10);
    evt.currentTarget.classList.add("active");
}

function closeDrawer() {
    document.getElementById("order-drawer").classList.remove("active");
    document.getElementById("drawer-overlay").classList.remove("active");
}

function openOrderDetails(orderId, recalculate = false) {
    currentOrderId = orderId;
    
    if (!recalculate) {
        document.getElementById("order-drawer").classList.add("active");
        document.getElementById("drawer-overlay").classList.add("active");
        
        document.getElementById("drawer-summary-content").innerHTML = "Loading...";
        document.getElementById("drawer-cutting-content").innerHTML = "Loading...";
        document.getElementById("drawer-glass-content").innerHTML = "Loading...";
        document.getElementById("drawer-hardware-content").innerHTML = "Loading...";
        
        // Open the first tab by default
        const firstTab = document.querySelector('.d-tab-btn');
        if(firstTab) firstTab.click();
    } else {
        document.getElementById("drawer-summary-content").innerHTML = "Recalculating...";
    }

    let url = `/order/${orderId}/`;
    if (recalculate) url += "?recalculate=true";

    fetch(url)
        .then(res => res.json())
        .then(data => {
            renderSummary(data);
            renderCutting(data);
            renderGlass(data);
            renderHardware(data);
            
            // Set the PDF link
            const pdfBtn = document.getElementById("download-pdf-btn");
            if (pdfBtn) {
                pdfBtn.href = `/order/${orderId}/pdf/`;
            }
        })
        .catch(err => {
            console.error("Error fetching order details", err);
            document.getElementById("drawer-summary-content").innerHTML = `<p style="color:var(--error)">Error loading data.</p>`;
        });
}

function renderSummary(data) {
    const html = `
        <div class="d-card">
            <div class="d-card-title">Order Info</div>
            <div style="font-size: 1.1rem; color: #fff;">${data.product} - ${data.typology} (${data.dimensions})</div>
            <div style="color: #9ca3af; margin-top: 4px;">Quantity: ${data.quantity}</div>
        </div>
        
        <div class="d-card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div class="d-card-title">Material Waste</div>
                <div class="d-card-value" style="color: ${data.summary.avg_waste > 10 ? '#ef4444' : '#10b981'}">${data.summary.avg_waste}%</div>
            </div>
            <div>
                <div class="d-card-title">Bars Used</div>
                <div class="d-card-value">${data.summary.total_bars_used}</div>
            </div>
        </div>

        <div class="d-card">
            <div class="d-card-title">Cost Breakdown (USD)</div>
            <table class="dark-table" style="margin-top: 10px;">
                <tr><td>Profile Material</td><td style="text-align:right">$${data.costs.profile.toFixed(2)}</td></tr>
                <tr><td>Glass</td><td style="text-align:right">$${data.costs.glass.toFixed(2)}</td></tr>
                <tr><td>Hardware</td><td style="text-align:right">$${data.costs.hardware.toFixed(2)}</td></tr>
                <tr><td>Labor</td><td style="text-align:right">$${data.costs.labor.toFixed(2)}</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.2); font-weight: bold; color: #fff;">
                    <td>Total Cost</td><td style="text-align:right">$${data.costs.total.toFixed(2)}</td>
                </tr>
            </table>
        </div>
    `;
    document.getElementById("drawer-summary-content").innerHTML = html;
}

function renderCutting(data) {
    let html = `
        <div class="d-card">
            <div class="d-card-title">Cutting List</div>
            <table class="dark-table" style="margin-top: 10px;">
                <tr><th>Profile</th><th>Length (mm)</th><th>Qty</th></tr>
    `;
    data.cutting_plan.cuts.forEach(c => {
        html += `<tr><td>${c.profile}</td><td>${c.length}</td><td>${c.quantity}</td></tr>`;
    });
    html += `</table></div>`;

    html += `<div class="d-card mt-4"><div class="d-card-title">Bar Optimization Visual</div>`;
    
    for (const [profile, bars] of Object.entries(data.cutting_plan.optimized)) {
        html += `<h4 style="margin-top:15px; font-size: 0.9rem; color:#fff;">${profile}</h4>`;
        bars.forEach((bar, idx) => {
            const wasteW = bar.waste_percentage;
            html += `<div class="bar-visual-container">
                        <div class="bar-title"><span>Bar ${idx + 1} (${bar.cuts.length} cuts)</span><span>Waste: ${wasteW}%</span></div>
                        <div class="bar-visual">`;
            bar.cuts.forEach(c => {
                const w = (c / 6000) * 100;
                html += `<div class="cut-segment" style="width: ${w}%" title="${c}mm"></div>`;
            });
            html += `<div class="waste-segment" style="width: ${wasteW}%" title="Waste ${bar.leftover}mm"></div>
                    </div></div>`;
        });
    }
    html += `</div>`;
    document.getElementById("drawer-cutting-content").innerHTML = html;
}

function renderGlass(data) {
    let html = `
        <div class="d-card">
            <div class="d-card-title">Glass Requirements</div>
            <table class="dark-table" style="margin-top: 10px;">
                <tr><th>Width (mm)</th><th>Height (mm)</th><th>Qty</th><th>Area (m²)</th></tr>
    `;
    data.glass.forEach(g => {
        const area = ((g.width / 1000) * (g.height / 1000)).toFixed(2);
        html += `<tr><td>${g.width}</td><td>${g.height}</td><td>${g.quantity}</td><td>${area}</td></tr>`;
    });
    html += `</table></div>`;
    document.getElementById("drawer-glass-content").innerHTML = html;
}

function renderHardware(data) {
    let html = `
        <div class="d-card">
            <div class="d-card-title">Hardware Requirements</div>
            <table class="dark-table" style="margin-top: 10px;">
                <tr><th>Component</th><th>Quantity</th></tr>
    `;
    data.hardware.forEach(h => {
        html += `<tr><td>${h.name}</td><td>${h.quantity}</td></tr>`;
    });
    html += `</table></div>`;
    document.getElementById("drawer-hardware-content").innerHTML = html;
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById("recalculate-btn");
    if(btn) {
        btn.addEventListener("click", () => {
            if(currentOrderId) {
                openOrderDetails(currentOrderId, true);
            }
        });
    }
});
