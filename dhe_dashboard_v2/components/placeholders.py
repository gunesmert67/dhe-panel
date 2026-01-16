import streamlit as st
import textwrap

def render_dummy_page(title):
    html_content = (
        f"""<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; text-align: center;">"""
        f"""    <div style="background: var(--glass-bg); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid var(--glass-border); padding: 3rem; border-radius: 16px; box-shadow: var(--shadow-md); max-width: 500px; width: 90%; display: flex; flex-direction: column; align-items: center;">"""
        f"""        <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.8; filter: drop-shadow(0 0 10px rgba(196, 18, 31, 0.5));">🚧</div>"""
        f"""        <h2 style="color: var(--text-primary); margin: 0; font-weight: 800; letter-spacing: -0.5px; text-transform: uppercase;">"""
        f"""            {title}"""
        f"""        </h2>"""
        f"""        <p style="color: var(--text-secondary); margin-top: 0.5rem; font-size: 1.1rem;">Bu modül şu anda geliştirme aşamasındadır.</p>"""
        f"""        <div style="margin-top: 2rem; padding: 1.5rem; background: var(--bg-secondary); border-radius: 8px; font-size: 0.95rem; border: 1px solid var(--border-color); width: 100%; text-align: left;">"""
        f"""            <div style="color: var(--text-primary); font-weight: 700; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 8px;">"""
        f"""                    <span style="color: #FACC15;">⚡</span> Yakında Gelecek Özellikler"""
        f"""            </div>"""
        f"""            <ul style="color: var(--text-secondary); margin: 0; padding-left: 1.2rem; line-height: 1.6;">"""
        f"""                <li>Kapsamlı raporlama ve analiz ekranları</li>"""
        f"""                <li>Dinamik veri giriş ve düzenleme formları</li>"""
        f"""                <li>Gerçek zamanlı süreç takibi ve bildirimler</li>"""
        f"""            </ul>"""
        f"""        </div>"""
        f"""        <div style="margin-top: 1.5rem; font-size: 0.8rem; color: var(--text-muted); opacity: 0.7;">"""
        f"""            DHE Endüstriyel Dashboard v2.3.0"""
        f"""        </div>"""
        f"""    </div>"""
        f"""</div>"""
    )
    st.markdown(html_content, unsafe_allow_html=True)
