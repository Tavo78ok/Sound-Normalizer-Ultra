#!/usr/bin/env python3

import sys, os, subprocess, re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel, QProgressBar, QHBoxLayout, QSlider, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

class ProcessWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished_batch = pyqtSignal()

    def __init__(self, files, target_db, cover_path=None):
        super().__init__()
        self.files = files
        self.target_db = target_db
        self.cover_path = cover_path
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        for i, (fin, fout) in enumerate(self.files):
            if not self._is_running: break

            self.progress.emit(i, 30, "Analizando volumen...")
            # Análisis
            check_cmd = f'ffmpeg -i "{fin}" -filter:a volumedetect -f null /dev/null'
            res = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            match = re.search(r"mean_volume: ([\-\d\.]+) dB", res.stderr)
            vol_info = f"{match.group(1)} dB" if match else "?? dB"

            # Normalización
            self.progress.emit(i, 60, "Normalizando...")
            cmd = f'ffmpeg -i "{fin}" -filter:a "loudnorm=i={self.target_db}" "{fout}" -y'
            proc = subprocess.run(cmd, shell=True, capture_output=True)

            if proc.returncode == 0:
                # Si el usuario seleccionó una carátula, la incrustamos
                if self.cover_path and os.path.exists(self.cover_path):
                    self.embed_custom_cover(fout)
                self.progress.emit(i, 100, f"Listo ({vol_info} -> {self.target_db} LUFS) ✅")
            else:
                self.progress.emit(i, 0, "Error ❌")

        self.finished_batch.emit()

    def embed_custom_cover(self, audio_path):
        try:
            audio = MP3(audio_path, ID3=ID3)
            with open(self.cover_path, 'rb') as f:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=f.read()))
            audio.save()
        except Exception as e:
            print(f"Error al incrustar carátula: {e}")

class SoundNormalizerUltra(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Normalizer Ultra - Custom Covers")
        self.resize(1000, 650)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.selected_cover = None

        layout = QVBoxLayout()

        # --- PANEL DE CONTROL SUPERIOR ---
        top_panel = QHBoxLayout()

        # Volumen
        vol_box = QVBoxLayout()
        self.label_vol = QLabel("Objetivo: -14 LUFS")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(-30, -5); self.slider.setValue(-14)
        self.slider.valueChanged.connect(lambda v: self.label_vol.setText(f"Objetivo: {v} LUFS"))
        vol_box.addWidget(self.label_vol); vol_box.addWidget(self.slider)
        top_panel.addLayout(vol_box, 2)

        # Selector de Carátula
        cover_box = QVBoxLayout()
        self.btn_cover = QPushButton("Seleccionar Carátula")
        self.btn_cover.clicked.connect(self.select_cover)
        self.cover_preview = QLabel("Sin Imagen")
        self.cover_preview.setFixedSize(80, 80)
        self.cover_preview.setStyleSheet("border: 1px solid #444; background: #000;")
        self.cover_preview.setScaledContents(True)
        cover_box.addWidget(self.btn_cover)
        cover_box.addWidget(self.cover_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        top_panel.addLayout(cover_box, 1)

        layout.addLayout(top_panel)

        # Tabla
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Archivo", "Progreso", "Estado / Análisis"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Botonera
        btns = QHBoxLayout()
        self.btn_add = QPushButton("Añadir Música"); self.btn_add.clicked.connect(self.add_files)
        self.btn_clear = QPushButton("Limpiar Lista"); self.btn_clear.clicked.connect(self.clear_list)
        self.btn_start = QPushButton("INICIAR"); self.btn_start.setStyleSheet("background-color: #0078d4; font-weight: bold;")
        self.btn_start.clicked.connect(self.start)

        for b in [self.btn_add, self.btn_clear, self.btn_start]: btns.addWidget(b)
        layout.addLayout(btns)

        container = QWidget(); container.setLayout(layout)
        self.setCentralWidget(container)
        self.queue = []

    def select_cover(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imágenes (*.jpg *.png *.jpeg)")
        if path:
            self.selected_cover = path
            self.cover_preview.setPixmap(QPixmap(path))
            self.btn_cover.setText("Carátula Cargada ✓")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Audios")
        for f in files:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(os.path.basename(f)))
            pbar = QProgressBar(); self.table.setCellWidget(row, 1, pbar)
            self.table.setItem(row, 2, QTableWidgetItem("Esperando..."))
            out = os.path.join(os.path.dirname(f), "ULTRA_" + os.path.basename(f))
            self.queue.append((f, out))

    def clear_list(self):
        self.table.setRowCount(0); self.queue = []; self.selected_cover = None
        self.cover_preview.clear(); self.cover_preview.setText("Sin Imagen")
        self.btn_cover.setText("Seleccionar Carátula")

    def start(self):
        if not self.queue: return
        self.worker = ProcessWorker(self.queue, self.slider.value(), self.selected_cover)
        self.worker.progress.connect(self.update_ui)
        self.worker.start()

    def update_ui(self, index, pct, status):
        bar = self.table.cellWidget(index, 1)
        if bar: bar.setValue(pct)
        self.table.setItem(index, 2, QTableWidgetItem(status))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Identidad de la aplicación para el sistema
    app.setApplicationName("sound-normalizer-ultra")

    if sys.platform == 'linux':
        # Sin el .desktop, como pide la advertencia de Qt
        app.setDesktopFileName("sound-normalizer-ultra")

    win = SoundNormalizerUltra()
    win.show()
    sys.exit(app.exec())

