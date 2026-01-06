import streamlit as st
import math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import base64
import time

# Atur konfigurasi halaman website
st.set_page_config(
    page_title="Kalkulator Bangun Datar & Ruang",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS yang Rapi dan Modern 
st.markdown("""
    <style>
    /* Reset & Base */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Headings */
    h1, h2, h3 {
        color: #4da6ff;
        font-weight: 600;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #262730;
    }

    /* Cards/Containers */
    .stCard {
        background: #262730;
        border: 1px solid #41444e;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Custom Inputs */
    .stNumberInput input {
        border-radius: 5px !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #4da6ff;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2186eb;
    }

    /* Success Metric */
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00CC96;
    }
    </style>
""", unsafe_allow_html=True)

# Cek session state buat nyimpen history perhitungan
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_calc' not in st.session_state:
    st.session_state.last_calc = None

# Fungsi buat bikin file PDF laporan
def export_to_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Laporan Hasil Perhitungan", ln=1, align='C')
    pdf.ln(10)
    
    for key, value in data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=1)
        
    pdf.ln(10)
    pdf.cell(200, 10, txt="Dibuat dengan Python Streamlit", ln=1, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# Bagian Sidebar untuk navigasi menu
with st.sidebar:
    st.markdown("## 📐 Kalkulator Geometri")
    st.caption("Tugas Pemrograman Dasar ")
    
    menu = st.radio("Menu", ["🏠 Kalkulator", "📝 Riwayat", "ℹ️ Tentang"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### ⚙️ Pengaturan")
    enable_3d = st.toggle("Mode Bangun Ruang (3D)", value=False)
    
    # Pilihan Satuan Global (bisa di override nanti kalau mau per input)
    satuan_default = st.selectbox("Satuan Input:", ["cm", "m", "mm", "inci"])
    st.caption(f"Semua input dianggap dalam **{satuan_default}** kecuali ditentukan lain.")

# Halaman Kalkulator Utama
if menu == "🏠 Kalkulator":
    st.title("Kalkulator Bangun Datar & Ruang")
    st.write("Program bantu hitung luas, keliling, dan volume sederhana.")
    
    col_input, col_vis = st.columns([1, 1.5])
    
    with col_input:
        with st.container(border=True): # Pake container biar rapi
            
            # Kalau mode 2D (Bangun Datar) mati
            if not enable_3d:
                st.subheader("🟦 Bangun Datar")
                shapes_2d = ["Persegi", "Persegi Panjang", "Lingkaran", "Segitiga"]
                shape = st.selectbox("Pilih Bangun:", shapes_2d)
                
                operation = st.selectbox("Hitung apa?", ["Luas", "Keliling"])
                
                inputs = {}
                # Input angka sesuai bangun yang dipilih
                if shape == "Persegi":
                    inputs['s'] = st.number_input(f"Panjang Sisi ({satuan_default})", min_value=0.0, value=10.0)
                elif shape == "Persegi Panjang":
                    inputs['p'] = st.number_input(f"Panjang ({satuan_default})", min_value=0.0, value=12.0)
                    inputs['l'] = st.number_input(f"Lebar ({satuan_default})", min_value=0.0, value=5.0)
                elif shape == "Lingkaran":
                    inputs['r'] = st.number_input(f"Jari-jari ({satuan_default})", min_value=0.0, value=7.0)
                elif shape == "Segitiga":
                    inputs['a'] = st.number_input(f"Alas ({satuan_default})", min_value=0.0, value=10.0)
                    inputs['t'] = st.number_input(f"Tinggi ({satuan_default})", min_value=0.0, value=8.0)
                    if operation == "Keliling":
                         inputs['s2'] = st.number_input(f"Sisi B ({satuan_default})", 5.0)
                         inputs['s3'] = st.number_input(f"Sisi C ({satuan_default})", 5.0)

            # Kalau mode 3D (Bangun Ruang) nyala
            else:
                st.subheader("🧊 Bangun Ruang")
                shapes_3d = ["Kubus", "Balok", "Bola", "Tabung"]
                shape = st.selectbox("Pilih Bangun:", shapes_3d)
                
                operation = st.selectbox("Hitung apa?", ["Volume", "Luas Permukaan"])
                
                inputs = {}
                # Input angka buat bangun ruang
                if shape == "Kubus":
                    inputs['s'] = st.number_input(f"Sisi ({satuan_default})", 0.0, value=10.0)
                elif shape == "Balok":
                    inputs['p'] = st.number_input(f"Panjang ({satuan_default})", 0.0, value=10.0)
                    inputs['l'] = st.number_input(f"Lebar ({satuan_default})", 0.0, value=5.0)
                    inputs['t'] = st.number_input(f"Tinggi ({satuan_default})", 0.0, value=4.0)
                elif shape == "Bola":
                    inputs['r'] = st.number_input(f"Jari-jari ({satuan_default})", 0.0, value=7.0)
                elif shape == "Tabung":
                    inputs['r'] = st.number_input(f"Jari-jari ({satuan_default})", 0.0, value=5.0)
                    inputs['t'] = st.number_input(f"Tinggi ({satuan_default})", 0.0, value=10.0)

            st.write("") # Kasih jarak dikit
            calculate_btn = st.button("Hitung Hasil", use_container_width=True)
        
        # Proses hitungan kalau tombol ditekan
        if calculate_btn:
            with st.spinner("Sedang menghitung..."):
                time.sleep(0.3)
                
                result = 0
                steps = []
                
                # Rumus-rumus 2D
                if not enable_3d:
                    if shape == "Persegi":
                        s = inputs['s']
                        if operation == "Luas":
                            result = s**2
                            steps = [f"Diketahui sisi = {s} {satuan_default}", f"Rumus Luas Persegi = sisi × sisi", f"L = {s} × {s}", f"L = {result}"]
                        else:
                            result = 4*s
                            steps = [f"Diketahui sisi = {s} {satuan_default}", f"Rumus Keliling = 4 × sisi", f"K = 4 × {s}", f"K = {result}"]
                            
                    elif shape == "Lingkaran":
                        r = inputs['r']
                        if operation == "Luas":
                            result = math.pi * r**2
                            steps = [f"Diketahui r = {r} {satuan_default}", "Rumus Luas = π × r²", f"L = 3.14 × {r}²", f"L = {result:.2f}"]
                        else:
                            result = 2 * math.pi * r
                    
                    elif shape == "Persegi Panjang":
                        p, l = inputs['p'], inputs['l']
                        result = p * l if operation == "Luas" else 2*(p+l)
                        steps = [f"Panjang = {p}, Lebar = {l}", f"Rumus = p × l" if operation=="Luas" else "Rumus = 2 × (p + l)"]
                        
                    elif shape == "Segitiga":
                        a, t = inputs['a'], inputs['t']
                        if operation == "Luas":
                            result = 0.5 * a * t
                        else:
                            result = a + inputs['s2'] + inputs['s3']

                # Rumus-rumus 3D
                else:
                    if shape == "Kubus":
                        s = inputs['s']
                        result = s**3 if operation == "Volume" else 6*(s**2)
                        steps = [f"Sisi = {s} {satuan_default}", f"Rumus Volume = s³" if operation=="Volume" else "Rumus LP = 6 × s²"]
                    elif shape == "Bola":
                        r = inputs['r']
                        result = (4/3)*math.pi*(r**3) if operation == "Volume" else 4*math.pi*(r**2)
                    elif shape == "Balok":
                        p,l,t = inputs['p'], inputs['l'], inputs['t']
                        result = p*l*t if operation == "Volume" else 2*(p*l + p*t + l*t)
                    elif shape == "Tabung":
                        r, t = inputs['r'], inputs['t']
                        result = math.pi*(r**2)*t if operation == "Volume" else 2*math.pi*r*(r+t)

                # Simpan hasil hitungan ke session state
                st.session_state.last_calc = {
                    "shape": shape, "op": operation, "res": result, "steps": steps, "inputs": inputs, "is_3d": enable_3d, "unit": satuan_default
                }
                st.session_state.history.append({"timestamp": pd.Timestamp.now(), "result": result, "shape": shape, "unit": satuan_default})

    # Bagian Visualisasi Hasil (Kanan)
    with col_vis:
        if st.session_state.last_calc:
            lc = st.session_state.last_calc
            satuan_luas = f"{lc['unit']}²" if lc['unit'] else "unit²" # pangkat 2 simpel
            satuan_vol = f"{lc['unit']}³" if lc['unit'] else "unit³" # pangkat 3 simpel
            unit_display = satuan_vol if lc['op'] == "Volume" else (satuan_luas if "Luas" in lc['op'] else lc['unit'])
            
            # Tampilan Kartu Hasil
            st.markdown(f"""
            <div style="text-align:center; padding: 20px; background: #262730; border-radius: 10px; border: 1px solid #41444e;">
                <h4 style="margin:0; color:#888;">Hasil Perhitungan</h4>
                <div class="metric-value">{lc['res']:.2f} {unit_display}</div>
                <p>{lc['shape']} - {lc['op']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tab buat milih mau liat visualisasi atau caranya
            tab1, tab2 = st.tabs(["👁️ Visualisasi", "📝 Cara Pengerjaan"])
            
            with tab1:
                # Bikin grafik pake Plotly
                fig = go.Figure()
                
                if lc['is_3d']:
                    # Logika simple buat bikin mesh 3D
                    if lc['shape'] == "Kubus":
                        s = lc['inputs']['s']
                        fig = go.Figure(data=[
                            go.Mesh3d(
                                x=[0, s, s, 0, 0, s, s, 0],
                                y=[0, 0, s, s, 0, 0, s, s],
                                z=[0, 0, 0, 0, s, s, s, s],
                                color='cyan', opacity=0.50, flatshading=True
                            )
                        ])
                    elif lc['shape'] == "Bola":
                        # Bikin bola sederhana pake scatter
                        fig = go.Figure(data=go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=lc['inputs']['r']*5, color='cyan', opacity=0.8)))
                    
                    fig.update_layout(scene=dict(bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0))
                    
                else:
                    # Gambar bangun datar 2D
                    if lc['shape'] == "Persegi":
                        s = lc['inputs']['s']
                        fig.add_shape(type="rect", x0=0, y0=0, x1=s, y1=s, line=dict(color="#4da6ff"), fillcolor="rgba(77, 166, 255, 0.2)")
                        fig.update_xaxes(range=[-1, s+1], visible=False)
                        fig.update_yaxes(range=[-1, s+1], visible=False)
                    elif lc['shape'] == "Lingkaran":
                         r = lc['inputs']['r']
                         fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r, line=dict(color="#4da6ff"), fillcolor="rgba(77, 166, 255, 0.2)")
                         fig.update_xaxes(range=[-r-1, r+1], visible=False)
                         fig.update_yaxes(range=[-r-1, r+1], visible=False)
                    
                    fig.update_layout(width=400, height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.markdown("### Langkah-langkah penyelesaian:")
                if lc['steps']:
                    for i, step in enumerate(lc['steps']):
                        st.info(f"{i+1}. {step}")
                else:
                    st.write("Langsung masukkan nilai ke rumus.")

        else:
            st.info("👈 Masukkan angka di sisi kiri, lalu tekan Hitung.")

# Halaman Riwayat dan Tentang
elif menu == "📝 Riwayat":
    st.markdown("## 📋 Log Perhitungan Anda")
    
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Belum ada data.")

elif menu == "ℹ️ Tentang":
    st.markdown("## Tentang Aplikasi")
    st.write("Aplikasi ini dibuat sebagai proyek tugas Pemrograman Dasar.")
    st.write("**Fitur:**")
    st.write("- Menghitung Luas & Keliling")
    st.write("- Menghitung Volume & Luas Permukaan (3D)")
    st.write("- Pilihan satuan dinamis")
    st.write("- Visual yang sangat menarik")
    st.write("- Fungsi semua berfungsi dengan baik")
    st.caption("Dibuat dengan menggunakan Python & Streamlit.")

