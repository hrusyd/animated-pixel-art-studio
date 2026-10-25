# Animated Pixel Art Studio

**Skill AI agent untuk mengubah brief menjadi animasi pixel art, video, dan source yang bisa diedit.**

[English](README.md) · [Skill agent](skills/animated-pixel-art-studio/SKILL.md) · [Format scene](skills/animated-pixel-art-studio/references/scene-format.md) · [Lisensi MIT](LICENSE)

![Contoh kafe pixel art](docs/gallery/rainy-cafe.png)

Jelaskan ide ke AI agent. Agent membuat sprite, komposisi, dan gerakan, lalu menjalankan renderer lokal. Repo ini berisi workflow dan alat render, bukan model text-to-video atau aplikasi editor grafis.

## Isi repo

- Skill lengkap: brief, art direction, animasi, ekspor, dan pemeriksaan visual.
- Scene JSON yang bisa diedit, sprite berbasis palet, PNG native, layer, dan keyframe posisi.
- Ekspor GIF, MP4, urutan PNG, poster, contact sheet, serta laporan render.
- Tiga demo original: kafe hujan, api unggun, dan karakter berjalan. Ada juga starter kosong.
- Render tanpa API key, GPU, atau model berbayar setelah dependensi terpasang.
- Pengujian otomatis dan konfigurasi GitHub Actions.

## Mulai

Pasang **Python 3.10+** dan Git:

```sh
git clone https://github.com/hrusyd/animated-pixel-art-studio.git
cd animated-pixel-art-studio
python -m venv .venv
```

Aktifkan environment:

| Sistem | Perintah |
| --- | --- |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

Jika aktivasi dibatasi, panggil Python langsung: `.venv\Scripts\python.exe studio.py doctor`. Jika nama Python di sistem adalah `python3`, gunakan itu untuk membuat environment.

```sh
python -m pip install -r requirements.txt
python studio.py doctor
python studio.py init --preset rainy-cafe --out work/scene-saya.json
python studio.py render work/scene-saya.json --out output/loop-pertama --formats png,gif
```

Buka `output/loop-pertama/animation.gif`. Edit scene dan render ke folder output baru. File output lama tidak ditimpa.

Untuk MP4, pasang [FFmpeg](https://ffmpeg.org/download.html) dengan encoder `libx264`, lalu pastikan `ffmpeg` tersedia di PATH:

```sh
python studio.py render work/scene-saya.json --out output/video-pertama --formats png,gif,mp4
```

Gunakan `--ffmpeg "lokasi/ffmpeg"` jika perlu. GIF/PNG tetap bisa dibuat tanpa FFmpeg.

## Pakai lewat AI agent

Berikan instruksi ini ke coding agent yang memiliki akses file dan terminal:

> Baca `skills/animated-pixel-art-studio/SKILL.md`. Buat animasi pixel art toko ramen kecil saat hujan, durasi 4 detik dan looping. Jendela hangat, kucing berkedip, palet konsisten, piksel tajam. Hasilkan GIF, MP4, dan source yang bisa diedit. Periksa contact sheet dan laporkan pengujian yang dilakukan.

Untuk host yang mendukung instalasi skill, salin seluruh folder skill ke direktori skill sesuai dokumentasi host:

```sh
python tools/install_skill.py --target /lokasi/direktori/skills-agent
```

Installer menolak menimpa instalasi lama dan tidak mengubah pengaturan agent. Folder skill sudah memuat renderer dan preset. Python/Pillow serta FFmpeg opsional tetap perlu tersedia. Agent yang hanya bisa chat tidak bisa menjalankan renderer ini.

Panggil `$animated-pixel-art-studio` jika host mendukung sintaks tersebut, atau minta agent membaca SKILL.md secara eksplisit. Repo tidak mengklaim integrasi otomatis dengan provider tertentu.

## Contoh brief lain

- Robot original 16x16 dengan empat pose berjalan dan pijakan kaki konsisten.
- Kebun terapung malam hari, 6 detik, vertikal 9:16 pada kanvas native 90x160.
- Api unggun 4 detik dengan traveler, perubahan bentuk api, dan percikan kecil.
- Susun sprite PNG milikku menjadi animasi 12 fps dengan palet asli.
- Buat cerita pixel art 12 detik dalam tiga shot, render terpisah, lalu gabungkan.

Preset adalah titik awal. Agent tetap harus mengubah aset, komposisi, dan gerakan sesuai brief baru.

## Demo

| Kafe hujan | Api unggun | Karakter berjalan |
| --- | --- | --- |
| ![Kafe](docs/gallery/rainy-cafe.gif) | ![Api unggun](docs/gallery/campfire.gif) | ![Berjalan](docs/gallery/walk-cycle.gif) |
| [MP4](docs/gallery/rainy-cafe.mp4) | [MP4](docs/gallery/campfire.mp4) | [MP4](docs/gallery/walk-cycle.mp4) |

Demo original dibuat lewat kode dan berlisensi MIT. Semuanya 4 detik pada 12 fps. GIF memakai resolusi native; PNG/MP4 diperbesar dengan kelipatan bulat.

### Contoh hasil penggunaan skill

![Robot Little Beacon](docs/gallery/robot.gif)

Agent terpisah memakai skill ini untuk membuat **Little Beacon**, robot melayang original selama 2 detik. [MP4](docs/gallery/robot.mp4) · [Scene yang bisa diedit](examples/robot/scene.json) · [Brief](examples/robot/brief.md). Ini satu uji penggunaan yang berhasil, bukan jaminan kualitas untuk semua agent atau prompt.

```sh
python studio.py render examples/robot/scene.json --out output/robot --formats png,gif,mp4
```

## Batasan

- Ini toolkit awal. Kualitas artistik tetap bergantung pada desain aset dan iterasi visual agent.
- MP4 tidak memiliki audio. Musik, subtitle, pemotongan sprite sheet, penyambungan shot, ComfyUI, model generatif, dan Aseprite bukan fitur bawaan.
- PNG adalah master lossless. Kompresi MP4 dapat mengubah tepi warna. GIF menggunakan satuan waktu centisecond.
- Label looping tidak menjamin sambungan mulus. Laporan otomatis tetap perlu dilengkapi pemeriksaan visual.
- Kanvas maksimal 512x512, maksimal 600 frame dan 40 juta native frame pixels, maksimal 64 warna. Pecah video besar menjadi beberapa shot.
- PNG impor harus memakai resolusi native, palet scene, dan alpha biner. Gunakan aset yang boleh kamu gunakan/distribusikan.

Detail teknis ada di [format scene](skills/animated-pixel-art-studio/references/scene-format.md), [art direction](skills/animated-pixel-art-studio/references/art-direction.md), dan [integrasi opsional](skills/animated-pixel-art-studio/references/integrations.md).

## Pengembangan

```sh
python -m unittest discover -s tests -v
python tools/build_examples.py
```

Tes metadata video membutuhkan FFmpeg/ffprobe dan dilewati bila keduanya tidak tersedia. CI memiliki job Linux dengan FFmpeg. Lihat hasil CI aktual pada tab Actions. Kode, dokumen, dan contoh original memakai lisensi MIT; dependensi pihak ketiga memakai lisensinya masing-masing.
