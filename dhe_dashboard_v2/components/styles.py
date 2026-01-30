import streamlit as st

def inject_css():
    """
    Premium DHE Industrial Theme - Steve Jobs Edition
    Minimalist, tutarlı ve kullanışlı arayüz.
    """
    theme = st.session_state.get("theme", "light")
    
    # ==========================================================================
    # DESIGN TOKENS
    # ==========================================================================
    
    # Typography Scale (Major Third - 1.25)
    typography = """
        --font-xs: 0.75rem;    /* 12px */
        --font-sm: 0.875rem;   /* 14px */
        --font-base: 1rem;     /* 16px */
        --font-lg: 1.125rem;   /* 18px */
        --font-xl: 1.25rem;    /* 20px */
        --font-2xl: 1.5rem;    /* 24px */
        --font-3xl: 2rem;      /* 32px */
        --font-4xl: 2.5rem;    /* 40px */
        
        /* Font Weights */
        --weight-normal: 400;
        --weight-medium: 500;
        --weight-semibold: 600;
        --weight-bold: 700;
        --weight-extrabold: 800;
        
        /* Line Heights */
        --leading-tight: 1.1;
        --leading-snug: 1.25;
        --leading-normal: 1.5;
        --leading-relaxed: 1.75;
    """
    
    # Spacing Scale (4px base)
    spacing = """
        --space-1: 0.25rem;    /* 4px */
        --space-2: 0.5rem;     /* 8px */
        --space-3: 0.75rem;    /* 12px */
        --space-4: 1rem;       /* 16px */
        --space-5: 1.25rem;    /* 20px */
        --space-6: 1.5rem;     /* 24px */
        --space-8: 2rem;       /* 32px */
        --space-10: 2.5rem;    /* 40px */
        --space-12: 3rem;      /* 48px */
    """
    
    # Transitions
    transitions = """
        --transition-fast: 150ms ease;
        --transition-base: 200ms ease;
        --transition-slow: 300ms ease;
    """
    
    # Border Radius
    radius = """
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-full: 9999px;
    """
    
    colors = """
            /* Backgrounds */
            --bg-primary: #F8FAFC;
            --bg-secondary: #F1F5F9;
            --bg-tertiary: #E2E8F0;
            --header-bg: #0F172A;
            
            /* Cards */
            --card-bg: #FFFFFF;
            --card-bg-hover: #FAFAFA;
            --card-border: #E2E8F0;
            --card-border-hover: #CBD5E1;
            
            /* Text */
            --text-primary: #1E293B;
            --text-secondary: #64748B;
            --text-muted: #94A3B8;
            --text-inverse: #F8FAFC;
            
            /* Borders */
            --border-color: #E2E8F0;
            --border-hover: #CBD5E1;
            
            /* Accent */
            --accent-primary: #DC2626;
            --accent-glow: rgba(220, 38, 38, 0.12);
            
            /* Shadows */
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
            --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
            
            /* Glass */
            --glass-bg: rgba(255, 255, 255, 0.9);
            --glass-border: rgba(255, 255, 255, 0.5);
            
            /* Status */
            --success: #059669;
            --warning: #D97706;
            --error: #DC2626;
            --info: #2563EB;
        """
    sidebar_bg = "#FFFFFF"
    sidebar_text = "#1E293B"

    css = f"""
    <style>
        /* =================================================================
           FONT IMPORTS
           ================================================================= */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* =================================================================
           CSS CUSTOM PROPERTIES
           ================================================================= */
        :root {{
            {typography}
            {spacing}
            {transitions}
            {radius}
            {colors}
        }}
        
        /* =================================================================
           GLOBAL RESET & BASE
           ================================================================= */
        .stApp {{
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            font-size: var(--font-base);
            line-height: var(--leading-normal);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* Hide Anchor Links */
        .stApp a.anchor-link {{
            display: none !important;
        }}
        [data-testid="stHeader"] a {{
            display: none !important;
        }}
        
        /* =================================================================
           LAYOUT
           ================================================================= */
        div.block-container {{
            padding: var(--space-8) var(--space-8) var(--space-12) var(--space-8) !important;
            max-width: 100% !important;
        }}
        
        /* =================================================================
           SIDEBAR
           ================================================================= */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid var(--border-color) !important;
        }}
        
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
            color: {sidebar_text} !important;
        }}
        
        /* =================================================================
           HEADER
           ================================================================= */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}
        
        .main-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--space-5) var(--space-8);
            margin: calc(var(--space-8) * -1) calc(var(--space-8) * -1) var(--space-8) calc(var(--space-8) * -1);
            background: var(--header-bg);
            border-bottom: 3px solid var(--accent-primary);
            box-shadow: var(--shadow-lg);
            border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        }}
        
        .header-title {{
            font-family: 'Inter', sans-serif;
            font-size: var(--font-lg);
            font-weight: var(--weight-bold);
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--text-inverse);
        }}
        
        .header-date {{
            font-family: 'Inter', monospace;
            font-size: var(--font-sm);
            font-weight: var(--weight-bold);
            color: white;
            background: var(--accent-primary);
            padding: var(--space-2) var(--space-4);
            border-radius: var(--radius-sm);
        }}
        
        /* =================================================================
           CARDS (BENTO STYLE)
           ================================================================= */
        .bento-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: var(--radius-lg);
            padding: var(--space-6);
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-base);
        }}
        
        .bento-card:hover {{
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        .card-label {{
            font-size: var(--font-sm);
            font-weight: var(--weight-semibold);
            color: var(--text-secondary);
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }}
        
        .card-value {{
            font-size: var(--font-3xl);
            font-weight: var(--weight-extrabold);
            color: var(--text-primary);
            line-height: var(--leading-tight);
            font-feature-settings: 'tnum' 1; /* Tabular numbers */
        }}
        
        .card-sub {{
            font-size: var(--font-sm);
            color: var(--text-muted);
            margin-top: var(--space-2);
        }}
        
        /* =================================================================
           SECTION TITLES
           ================================================================= */
        .section-title {{
            font-size: var(--font-lg);
            font-weight: var(--weight-bold);
            color: var(--text-primary);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: var(--space-3);
            margin: var(--space-8) 0 var(--space-6) 0;
            display: flex;
            align-items: center;
            gap: var(--space-3);
        }}
        
        .section-title::before {{
            content: '';
            display: block;
            width: 4px;
            height: 24px;
            background: var(--accent-primary);
            border-radius: 2px;
        }}
        
        /* =================================================================
           BUTTONS
           ================================================================= */
        .stButton > button {{
            background: var(--card-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            font-weight: var(--weight-medium) !important;
            font-size: var(--font-sm) !important;
            padding: var(--space-2) var(--space-4) !important;
            transition: all var(--transition-fast) !important;
        }}
        
        .stButton > button:hover {{
            border-color: var(--accent-primary) !important;
            background: var(--card-bg-hover) !important;
        }}
        
        .stButton > button[kind="primary"] {{
            background: var(--accent-primary) !important;
            color: white !important;
            border: none !important;
        }}
        
        /* =================================================================
           DATA TABLES
           ================================================================= */
        div[data-testid="stDataFrame"] {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-lg) !important;
            overflow: hidden !important;
        }}
        
        /* Table Headers */
        div[data-testid="stDataFrame"] div[role="columnheader"] {{
            padding: var(--space-4) var(--space-3) !important;
            font-weight: var(--weight-semibold) !important;
            font-size: var(--font-xs) !important;
            color: var(--text-secondary) !important;
            background-color: var(--bg-secondary) !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid var(--border-color) !important;
        }}
        
        /* Table Cells */
        div[data-testid="stDataFrame"] div[role="cell"] {{
            padding: var(--space-3) !important;
            color: var(--text-primary) !important;
            font-size: var(--font-sm) !important;
            border-bottom: 1px solid var(--border-color) !important;
            font-feature-settings: 'tnum' 1;
        }}
        
        /* Row Hover */
        div[data-testid="stDataFrame"] div[role="row"]:hover div[role="cell"] {{
            background-color: var(--bg-secondary) !important;
        }}
        
        /* =================================================================
           FORM ELEMENTS
           ================================================================= */
        label, 
        .stSelectbox label, 
        .stTextInput label,
        .stMultiSelect label {{
            color: var(--text-primary) !important;
            font-weight: var(--weight-medium) !important;
            font-size: var(--font-sm) !important;
        }}
        
        /* Selectbox Container */
        .stSelectbox > div > div {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
        }}
        
        .stSelectbox > div > div:hover {{
            border-color: var(--accent-primary) !important;
        }}
        
        /* MultiSelect Container */
        .stMultiSelect > div > div {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
        }}
        
        .stMultiSelect > div > div:hover {{
            border-color: var(--accent-primary) !important;
        }}
        
        /* MultiSelect Pills */
        .stMultiSelect span[data-baseweb="tag"] {{
            background-color: var(--accent-primary) !important;
            border-radius: var(--radius-sm) !important;
        }}
        
        /* Text Input */
        .stTextInput input {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
        }}
        
        .stTextInput input:focus {{
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 2px var(--accent-glow) !important;
        }}
        
        /* =================================================================
           TABS
           ================================================================= */
        button[data-baseweb="tab"] {{
            font-weight: var(--weight-semibold) !important;
            font-size: var(--font-sm) !important;
            color: var(--text-secondary) !important;
            transition: color var(--transition-fast) !important;
        }}
        
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: var(--accent-primary) !important;
        }}
        
        /* =================================================================
           METRICS & KPIs
           ================================================================= */
        [data-testid="stMetricValue"] {{
            font-size: var(--font-2xl) !important;
            font-weight: var(--weight-extrabold) !important;
            color: var(--text-primary) !important;
            font-feature-settings: 'tnum' 1;
        }}
        
        [data-testid="stMetricDelta"] {{
            font-size: var(--font-sm) !important;
            font-weight: var(--weight-semibold) !important;
        }}
        
        /* =================================================================
           EXPANDER
           ================================================================= */
        details {{
            background: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-lg) !important;
        }}
        
        details summary {{
            font-weight: var(--weight-semibold) !important;
            color: var(--text-primary) !important;
        }}
        
        /* =================================================================
           TABS (Baseweb Overlay)
           ================================================================= */
        div[data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: transparent;
            padding: 10px 0;
            border-bottom: none;
        }}

        button[data-baseweb="tab"] {{
            background-color: var(--bg-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.75rem 1.5rem !important;
            color: var(--text-secondary) !important;
            font-weight: var(--weight-semibold) !important;
            transition: all var(--transition-base) !important;
            flex: 1; /* Expand to fill */
        }}

        button[data-baseweb="tab"]:hover {{
            background-color: var(--card-bg) !important;
            border-color: var(--accent-primary) !important;
            color: var(--accent-primary) !important;
            box-shadow: var(--shadow-sm);
            transform: translateY(-2px);
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: var(--accent-primary) !important;
            color: white !important;
            border-color: var(--accent-primary) !important;
            box-shadow: 0 4px 6px -1px var(--accent-glow);
        }}
        
        div[data-baseweb="tab-highlight"] {{
            display: none;
        }}

        /* =================================================================
           TABLES (Premium Style)
           ================================================================= */
        [data-testid="stDataFrame"] table tr th, 
        [data-testid="stDataFrame"] table tr td {{
            padding-top: 0.8rem !important;
            padding-bottom: 0.8rem !important;
            border-bottom: 1px solid var(--border-color) !important;
            border-top: none !important;
            border-left: none !important;
            border-right: none !important;
        }}
        
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border-color) !important;
            box-shadow: var(--shadow-sm) !important;
        }}

        /* =================================================================
           RADIO BUTTONS (Pill Style)
           ================================================================= */
        div.row-widget.stRadio > div[role="radiogroup"] {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 4px;
            display: inline-flex;
            gap: 4px;
        }}
        
        div.row-widget.stRadio > div[role="radiogroup"] label {{
            background-color: transparent !important;
            border: none;
            flex: 1;
            text-align: center;
            border-radius: var(--radius-sm);
            padding: 4px 12px;
            color: var(--text-secondary) !important;
            cursor: pointer;
            transition: all var(--transition-fast);
        }}
        
        div.row-widget.stRadio > div[role="radiogroup"] label:hover {{
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }}
        
        div.row-widget.stRadio > div[role="radiogroup"] label[data-checked="true"] {{
            background-color: var(--accent-primary) !important;
            color: white !important;
            font-weight: var(--weight-semibold);
            box-shadow: var(--shadow-sm);
        }}

        /* =================================================================
           SCROLLBAR (Subtle)
           ================================================================= */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}
        
        /* =================================================================
           SIDEBAR TOGGLE
           ================================================================= */
        button[data-testid="stSidebarCollapseButton"] {{
            background-color: transparent !important;
            color: var(--text-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 50% !important; /* Circle instead of box for cleaner look, or small radius for box */
            width: 32px !important;
            height: 32px !important;
            transition: all 0.2s ease !important;
        }}

        button[data-testid="stSidebarCollapseButton"]:hover {{
            background-color: var(--card-bg) !important;
            color: var(--accent-primary) !important;
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 10px var(--accent-glow) !important;
            transform: scale(1.1);
        }}
        
    </style>
    """
    print("CSS Injected")
    st.markdown(css, unsafe_allow_html=True)


def inject_sidebar_style(theme: str = "light"):
    """
    Sidebar ve Navigasyon Buton Stilleri
    App.py içindeki karmaşık CSS bloklarını buraya taşıyoruz.
    """
    # Light Mode (Clean / Corporate) - Enforced
    # Light Mode (Clean / Corporate) - Enforced
    sb_bg = "#F8FAFC" # Slate 50
    sb_border = "#E2E8F0" # Slate 200
    
    # Text Colors
    text_norm = "#475569" # Slate 600
    text_hover = "#1E293B" # Slate 800
    text_active = "#C4121F" # DHE Red
    
    # Button Backgrounds
    btn_hover_bg = "#F1F5F9" # Slate 100
    btn_active_bg = "#FFFFFF"
    
    # Decoration
    active_border_color = "#C4121F" # Red
    group_title_color = "#94A3B8"
    hr_color = "#E2E8F0"

    # --- EKSTRA SAYFA STİLLERİ ---
    extra_styles = """
        /* Hero Section (Landing Page) */
        .hero-container {
            padding: 2rem;
            border-radius: 12px;
            border-left: 5px solid var(--accent-primary);
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-base);
        }
        
        /* Action Button Card (Landing Page) */
        .action-card {
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            text-align: center;
            height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-bottom: 0.5rem;
            background-color: var(--card-bg);
            transition: border-color var(--transition-fast);
        }
        .action-card:hover {
            border-color: var(--accent-primary);
        }
        
        /* CRM Segment Badges */
        .segment-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
    """

    css = f"""
    <style>
        /* 1. SIDEBAR ZEMİNİ */
        section[data-testid="stSidebar"] {{
            background-color: {sb_bg} !important;
            border-right: 1px solid {sb_border};
        }}
        
        /* 2. BUTON STİLLERİ (RESET VE ÖZELLEŞTİRME) */
        /* Pasif Butonlar (Secondary) */
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background-color: transparent;
            color: {text_norm};
            border: none;
            text-align: left;
            padding: 0.5rem 0.75rem;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            width: 100%;
            border-radius: 6px;
            margin: 0 !important;
        }}
        
        /* Hover Efekti */
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
            background-color: {btn_hover_bg};
            color: {text_hover};
            border: none;
            padding-left: 1rem; /* Sağa kayma efekti */
        }}

        /* Aktif Buton (Primary) */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background-color: {btn_active_bg} !important;
            color: {text_active} !important;
            border: 1px solid {sb_border}; /* Light modda border olsun */
            border-left: 4px solid {active_border_color} !important;
            text-align: left;
            padding: 0.5rem 0.75rem;
            font-weight: 700;
            font-size: 0.9rem;
            border-radius: 0 6px 6px 0;
            width: 100%;
            margin: 0 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        /* Buton Focus Border Kaldırma */
        button:focus {{
            outline: none !important;
            box-shadow: none !important;
        }}

        /* 3. GRUP BAŞLIKLARI VE METİNLER */
        .sidebar-group-title {{
            color: {group_title_color};
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            padding-left: 0.75rem;
        }}
        
        /* 4. SEPARATORS */
        hr {{
            border-color: {hr_color} !important;
            margin: 1rem 0 !important;
        }}
        
        /* 5. LOGO ALANI */
        .sidebar-logo-container {{
            padding: 1.5rem 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            border-bottom: 1px solid {hr_color};
            margin-bottom: 0.5rem;
        }}
        
        /* Sidebar Padding Reset */
        div[data-testid="stSidebar"] div.block-container {{
            padding-top: 0rem;
            padding-bottom: 0rem;
        }}
        div[data-testid="stVerticalBlock"] {{
            gap: 0.2rem;
        }}
        

        /* =================================================================
           LOGIN SCREEN
           ================================================================= */
        .login-container {{
            max_width: 400px;
            margin: 100px auto;
            padding: 2rem;
            border-radius: var(--radius-lg);
            background-color: var(--card-bg);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            text-align: center;
        }}



        /* =================================================================
           SIDEBAR TOGGLE BUTTON (Custom Red & Navy)
           ================================================================= */
        [data-testid="stSidebarCollapsedControl"] {{
            background-color: #0F172A !important; /* Navy Background */
            border-radius: 50% !important;
            border: 2px solid #DC2626 !important; /* Red Border */
            width: 2.5rem !important;
            height: 2.5rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin-left: 1rem !important;
            margin-top: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }}
        
        [data-testid="stSidebarCollapsedControl"]:hover {{
            background-color: #DC2626 !important; /* Red Background on Hover */
            border-color: #DC2626 !important;
            box-shadow: 0 0 15px rgba(220, 38, 38, 0.6) !important;
            transform: scale(1.05);
        }}

        [data-testid="stSidebarCollapsedControl"] svg {{
            fill: #DC2626 !important; /* Red Icon */
            stroke: #DC2626 !important;
        }}
        
        [data-testid="stSidebarCollapsedControl"]:hover svg {{
            fill: white !important; /* White Icon on Hover */
            stroke: white !important;
        }}

        {extra_styles}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
