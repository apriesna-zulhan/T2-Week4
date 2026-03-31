"""
Aplikasi Drawing Canvas - PySide6

Nama : Apriesna Zulhan
NIM  : F1D02310100
Kelas: Pemvis - C
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QSizePolicy,
    QMessageBox, QStatusBar, QMainWindow
)
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import (
    QPainter, QPen, QColor, QPixmap, QCursor
)


# Konstanta
WARNA_PILIHAN = [
    ("#e74c3c", "Merah"),
    ("#2ecc71", "Hijau"),
    ("#3498db", "Biru"),
    ("#f39c12", "Kuning"),
    ("#9b59b6", "Ungu"),
    ("#1abc9c", "Toska"),
    ("#e67e22", "Oranye"),
    ("#2c3e50", "Hitam"),
]


# ─── Widget Kanvas 
class KanvasGambar(QWidget):

    # Custom signal: koordinat mouse real-time
    posisi_berubah = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(800, 480)
        self.setCursor(QCursor(Qt.CrossCursor))
        self.setMouseTracking(True)          

        self._pixmap = QPixmap(self.size())
        self._pixmap.fill(Qt.white)

        self._menggambar = False
        self._titik_sebelumnya = QPoint()

        self._warna = QColor(WARNA_PILIHAN[0][0])
        self._ukuran = 5

    # Slot publik 
    def terima_warna(self, hex_warna: str):
        """Slot: menerima hex warna dari custom signal TombolWarna."""
        self._warna = QColor(hex_warna)

    def terima_ukuran(self, ukuran: int):
        """Slot: menerima ukuran brush dari signal QSlider.valueChanged."""
        self._ukuran = ukuran

    def bersihkan_kanvas(self):
        """Hapus seluruh isi kanvas."""
        self._pixmap.fill(Qt.white)
        self.update()

    # Resize
    def resizeEvent(self, event):
        baru = QPixmap(self.size())
        baru.fill(Qt.white)
        painter = QPainter(baru)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.end()
        self._pixmap = baru
        super().resizeEvent(event)

    # Mouse Events 
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._menggambar = True
            self._titik_sebelumnya = event.position().toPoint()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        # StatusBar menerima koordinat real-time
        self.posisi_berubah.emit(pos.x(), pos.y())

        if self._menggambar and (event.buttons() & Qt.LeftButton):
            painter = QPainter(self._pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(
                self._warna, self._ukuran,
                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            painter.setPen(pen)
            painter.drawLine(self._titik_sebelumnya, pos)
            painter.end()
            self._titik_sebelumnya = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._menggambar = False

    def mouseDoubleClickEvent(self, event):
        """Double-click → clear canvas langsung tanpa konfirmasi."""
        if event.button() == Qt.LeftButton:
            self._menggambar = False
            self.bersihkan_kanvas()

    # paintEvent (override) 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)


# Tombol Warna 
class TombolWarna(QPushButton):
    """
    Tombol bulat pemilih warna.

    Custom Signal:
        warna_dipilih(str) — mengirim hex warna ke kanvas saat diklik.
    """

    warna_dipilih = Signal(str)

    def __init__(self, hex_warna: str, nama: str, parent=None):
        super().__init__(parent)
        self.hex_warna = hex_warna
        self.nama = nama
        self.setFixedSize(28, 28)
        self.setToolTip(nama)
        self._terpilih = False
        self._terapkan_style()
        self.clicked.connect(lambda: self.warna_dipilih.emit(self.hex_warna))

    def set_terpilih(self, status: bool):
        self._terpilih = status
        self._terapkan_style()

    def _terapkan_style(self):
        border = "3px solid #ffffff" if self._terpilih else "2px solid #555555"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.hex_warna};
                border: {border};
                border-radius: 14px;
            }}
            QPushButton:hover {{
                border: 2px solid #ffffff;
            }}
        """)


# Jendela Utama 
class MainWindow(QMainWindow):
    """Jendela utama aplikasi Drawing Canvas."""

    def __init__(self):
        super().__init__()
        self._tombol_warna_list: list[TombolWarna] = []
        self._tombol_aktif: TombolWarna | None = None
        self._nama_warna_aktif = WARNA_PILIHAN[0][1]
        self._ukuran_aktif = 5
        self.init_ui()
        self.setup_connections()

    # ── UI ──────
    def init_ui(self):
        self.setWindowTitle("Drawing Canvas")
        self.resize(1000, 640)
        self.setMinimumSize(700, 500)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2c3e50;
                font-family: Arial, sans-serif;
                font-size: 13px;
                color: #ecf0f1;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 13px;
            }
            QPushButton#btnBersihkan {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btnBersihkan:hover   { background-color: #c0392b; }
            QPushButton#btnBersihkan:pressed { background-color: #a93226; }
            QSlider::groove:horizontal {
                height: 4px;
                background: #7f8c8d;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #4da6e8;
                border: none;
                width: 14px; height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #4da6e8;
                border-radius: 2px;
            }
            QStatusBar {
                background-color: #1a252f;
                color: #7f8c8d;
                font-size: 12px;
                border-top: 1px solid #34495e;
            }
            QMessageBox {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
        """)

        # ── Toolbar 
        toolbar_widget = QWidget()
        toolbar_widget.setFixedHeight(50)
        toolbar_widget.setStyleSheet("""
            QWidget {
                background-color: #1a252f;
                border-bottom: 1px solid #34495e;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(14, 0, 14, 0)
        toolbar_layout.setSpacing(10)

        lbl_warna = QLabel("Warna:")
        lbl_warna.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        toolbar_layout.addWidget(lbl_warna)

        # Buat tombol warna & sambungkan custom signal-nya
        for hex_w, nama in WARNA_PILIHAN:
            btn = TombolWarna(hex_w, nama)
            # Custom signal TombolWarna.warna_dipilih
            btn.warna_dipilih.connect(
                lambda h=hex_w, b=btn: self._pilih_warna(h, b)
            )
            self._tombol_warna_list.append(btn)
            toolbar_layout.addWidget(btn)

        # Aktifkan warna pertama secara default
        self._tombol_aktif = self._tombol_warna_list[0]
        self._tombol_aktif.set_terpilih(True)

        toolbar_layout.addSpacing(20)

        lbl_ukuran = QLabel("Ukuran:")
        lbl_ukuran.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        toolbar_layout.addWidget(lbl_ukuran)

        # QSlider untuk ukuran brush
        self.slider_ukuran = QSlider(Qt.Horizontal)
        self.slider_ukuran.setRange(1, 30)
        self.slider_ukuran.setValue(self._ukuran_aktif)
        self.slider_ukuran.setFixedWidth(130)
        toolbar_layout.addWidget(self.slider_ukuran)

        self.lbl_nilai_ukuran = QLabel(f"{self._ukuran_aktif}px")
        self.lbl_nilai_ukuran.setStyleSheet(
            "color: #bdc3c7; font-size: 12px; min-width: 32px;"
        )
        toolbar_layout.addWidget(self.lbl_nilai_ukuran)
        toolbar_layout.addStretch()

        self.btn_bersihkan = QPushButton("✕  Bersihkan")
        self.btn_bersihkan.setObjectName("btnBersihkan")
        self.btn_bersihkan.setFixedHeight(34)
        toolbar_layout.addWidget(self.btn_bersihkan)

        # Kanvas 
        self.kanvas = KanvasGambar()

        # Layout tengah 
        pusat = QWidget()
        pusat_layout = QVBoxLayout(pusat)
        pusat_layout.setContentsMargins(0, 0, 0, 0)
        pusat_layout.setSpacing(0)
        pusat_layout.addWidget(toolbar_widget)
        pusat_layout.addWidget(self.kanvas)
        self.setCentralWidget(pusat)

        # QStatusBar 
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_koordinat = QLabel("X: 0  |  Y: 0")
        self.lbl_info_brush = QLabel(
            f"Warna: {self._nama_warna_aktif}  |  Ukuran: {self._ukuran_aktif}px"
        )
        self.lbl_hint = QLabel("Double-click kanvas untuk clear cepat")
        self.lbl_hint.setStyleSheet("color: #4a5568; font-size: 11px;")

        self.status_bar.addWidget(self.lbl_koordinat)
        self.status_bar.addWidget(QLabel("   |   "))
        self.status_bar.addWidget(self.lbl_info_brush)
        self.status_bar.addPermanentWidget(self.lbl_hint)

        self._center_on_screen()

    # Connections 
    def setup_connections(self):
        # Custom signal kanvas.posisi_berubah
        self.kanvas.posisi_berubah.connect(self._update_koordinat)

        # kanvas + label
        self.slider_ukuran.valueChanged.connect(self._ubah_ukuran)

        # konfirmasi QMessageBox
        self.btn_bersihkan.clicked.connect(self._konfirmasi_bersihkan)

    # ── Slots
    def _pilih_warna(self, hex_warna: str, tombol: TombolWarna):
        """Ganti warna aktif; kirim ke kanvas via slot terima_warna."""
        self._tombol_aktif.set_terpilih(False)
        tombol.set_terpilih(True)
        self._tombol_aktif = tombol
        self._nama_warna_aktif = tombol.nama
        self.kanvas.terima_warna(hex_warna)   # ← slot kanvas
        self._refresh_info_brush()

    def _ubah_ukuran(self, nilai: int):
        """Kirim ukuran brush ke kanvas via slot terima_ukuran."""
        self._ukuran_aktif = nilai
        self.lbl_nilai_ukuran.setText(f"{nilai}px")
        self.kanvas.terima_ukuran(nilai)  
        self._refresh_info_brush()

    def _update_koordinat(self, x: int, y: int):
        """
        Terima custom signal posisi_berubah dari KanvasGambar
        → tampilkan koordinat real-time di QStatusBar.
        """
        self.lbl_koordinat.setText(f"X: {x}  |  Y: {y}")

    def _refresh_info_brush(self):
        self.lbl_info_brush.setText(
            f"Warna: {self._nama_warna_aktif}  |  Ukuran: {self._ukuran_aktif}px"
        )

    def _konfirmasi_bersihkan(self):
        """Tampilkan QMessageBox konfirmasi sebelum clear canvas."""
        jawaban = QMessageBox.question(
            self,
            "Konfirmasi Bersihkan",
            "Apakah Anda yakin ingin menghapus seluruh gambar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if jawaban == QMessageBox.Yes:
            self.kanvas.bersihkan_kanvas()

    # Helper 
    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

def main():
    """Entry point aplikasi."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()