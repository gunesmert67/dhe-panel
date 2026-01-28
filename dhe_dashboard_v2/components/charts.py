import streamlit.components.v1 as components
import json
import streamlit as st

from typing import Dict, Any, Optional

def render_chartjs(chart_type: str, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None, height: int = 300, key: Optional[str] = None, currency_symbol: str = ""):
    """
    Renders a Chart.js chart using Streamlit Components.
    """
    if options is None:
        options = {}
    
    # TEMA ENTEGRASYONU
    current_theme = st.session_state.get("theme", "light")
    is_dark = current_theme == "dark"
    
    # Renk Paletleri
    text_color = "#E5E7EB" if is_dark else "#374151"
    grid_color = "#374151" if is_dark else "#E5E7EB"
    tooltip_bg = "rgba(0, 0, 0, 0.9)" if is_dark else "rgba(255, 255, 255, 0.95)"
    tooltip_text = "#fff" if is_dark else "#000"
    
    default_options = {
        "responsive": True,
        "maintainAspectRatio": False,
        "plugins": {
            "legend": {"labels": {"color": text_color, "font": {"family": "Inter"}}},
            "tooltip": {
                "backgroundColor": tooltip_bg,
                "titleColor": tooltip_text,
                "bodyColor": tooltip_text,
                "borderColor": "#C4121F",
                "borderWidth": 1,
                "padding": 10
            }
        },
        "scales": {
            "x": {"grid": {"color": grid_color}, "ticks": {"color": text_color}},
            "y": {"grid": {"color": grid_color}, "ticks": {"color": text_color}}
        }
    }
    
    # Merge Options (Recursive merge would be better but simple update is fine for now)
    final_options = default_options.copy()
    if options:
        # Shallow merge - user options overwrite defaults top-level
        # For deeper merging, we would need a helper, but let's assume user passes full structures if needed
        # Or simple overrides:
        final_options.update(options)
        
        # Re-apply theme criticals if user didn't specify
        if "scales" not in options:
             final_options["scales"] = default_options["scales"]
        if "plugins" not in options:
             final_options["plugins"] = default_options["plugins"]
    
    data_json = json.dumps(data)
    options_json = json.dumps(final_options)
    
    html_code = f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
        <style>
            body {{ margin: 0; overflow: hidden; height: {height}px; }}
            .chart-box {{ width: 100%; height: 100%; }}
        </style>
    </head>
    <body>
        <div class="chart-box">
            <canvas id="myChart"></canvas>
        </div>
        <script>
            // Global Defaults
            Chart.defaults.font.family = 'Inter';
            
            // Register DataLabels Plugin
            if (typeof ChartDataLabels !== 'undefined') {{
                Chart.register(ChartDataLabels);
                // Disable by default so it doesn't show on all charts
                Chart.defaults.set('plugins.datalabels', {{ display: false }});
            }}
            
            const ctx = document.getElementById('myChart');
            const chartData = {data_json};
            const chartOptions = {options_json};

            // Custom Tooltip Callback for Currency
            chartOptions.plugins = chartOptions.plugins || {{}};
            chartOptions.plugins.tooltip = chartOptions.plugins.tooltip || {{}};
            chartOptions.plugins.tooltip.callbacks = chartOptions.plugins.tooltip.callbacks || {{}};
            
            chartOptions.plugins.tooltip.callbacks.label = function(context) {{
                let label = context.dataset.label || '';
                if (label) {{
                    label += ': ';
                }}
                
                // Determine value based on chart orientation
                let val = context.parsed.y;
                if (chartOptions.indexAxis === 'y') {{
                    val = context.parsed.x;
                }}
                
                if (val !== null && val !== undefined) {{
                    // Format number and append symbol
                    // Using tr-TR locale for formatting (dots for thousands)
                    const formatted = val.toLocaleString('tr-TR', {{ minimumFractionDigits: 0, maximumFractionDigits: 0 }});
                    label += formatted + ' {currency_symbol}'; 
                }}
                return label;
            }};

            new Chart(ctx, {{
                type: '{chart_type}',
                data: chartData,
                options: chartOptions
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)


def get_themed_chart_options(chart_type: str = "line") -> dict:
    """
    Tema uyumlu varsayılan chart options döndürür.
    
    Args:
        chart_type: Grafik türü (line, bar, pie vb.)
    
    Returns:
        dict: Chart.js options objesi
    """
    from core.utils import get_theme_colors
    colors = get_theme_colors()
    
    base_options = {
        "maintainAspectRatio": False,
        "plugins": {
            "legend": {"display": False},
            "tooltip": {
                "backgroundColor": "#1F2937" if colors["is_dark"] else "#FFFFFF",
                "titleColor": "#F9FAFB" if colors["is_dark"] else "#111827",
                "bodyColor": "#F9FAFB" if colors["is_dark"] else "#6B7280",
                "borderColor": "rgba(255,255,255,0.1)" if colors["is_dark"] else "#E5E7EB",
                "borderWidth": 1,
                "padding": 10
            }
        },
        "scales": {
            "x": {
                "ticks": {"color": colors["text_color"], "font": {"family": "'Inter', 'Roboto', sans-serif"}},
                "grid": {"color": colors["grid_color"]}
            },
            "y": {
                "ticks": {"color": colors["text_color"], "font": {"family": "'Inter', 'Roboto', sans-serif"}},
                "grid": {"color": colors["grid_color"]},
                "beginAtZero": True
            }
        }
    }
    
    return base_options
