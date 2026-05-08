STRINGS: dict[str, str] = {
    # ── Butonlar ──────────────────────────────────────────────────────────────
    "btn_open_images":  "Resim Aç",
    "btn_open_folder":  "Klasör Aç",
    "btn_open_pdf":     "PDF Aç",
    "btn_scan_camera":  "Kamera",
    "btn_paste":        "Yapıştır",
    "btn_generate_qr":  "QR Oluştur",
    "btn_copy_all":     "Tümünü Kopyala",
    "btn_save_txt":     "TXT Kaydet",
    "btn_clear":        "Temizle",
    "btn_browse":       "Gözat",
    "btn_close":        "Kapat",

    # ── Araç ipuçları ─────────────────────────────────────────────────────────
    "tip_open_images":  "Bir veya daha fazla QR kod resmi aç",
    "tip_open_folder":  "Klasördeki tüm resimleri tara",
    "tip_open_pdf":     "PDF'ten QR kodları çıkar",
    "tip_scan_camera":  "Web kamerası ile tara",
    "tip_paste":        "Panodaki resimden QR kod oku",
    "tip_generate_qr":  "Metin veya URL'den QR kod oluştur",
    "tip_copy_all":     "Tüm sonuçları panoya kopyala",
    "tip_save_txt":     "Sonuçları düz metin olarak kaydet",
    "tip_clear":        "Tüm sonuçları temizle",

    # ── Menü ──────────────────────────────────────────────────────────────────
    "menu_file":            "Dosya",
    "menu_open_images":     "Resim Aç",
    "menu_open_folder":     "Klasör Aç",
    "menu_open_pdf":        "PDF Aç",
    "menu_scan_camera":     "Kameradan Tara",
    "menu_paste":           "Panodan Yapıştır",
    "menu_save_txt":        "TXT Olarak Kaydet",
    "menu_save_csv":        "CSV Olarak Kaydet",
    "menu_save_json":       "JSON Olarak Kaydet",
    "menu_exit":            "Çıkış",
    "menu_tools":           "Araçlar",
    "menu_generate_qr":     "QR Kod Oluştur",
    "menu_edit":            "Düzen",
    "menu_copy_all":        "Tümünü Kopyala",
    "menu_clear":           "Temizle",
    "menu_settings":        "Ayarlar",
    "menu_help":            "Yardım",
    "menu_history":         "Oturum Geçmişi",
    "menu_upgrade":         "Güncelle",
    "menu_check_updates":   "Güncelleme Kontrol Et",
    "menu_version":         "Sürüm",

    # ── Kısayollar ────────────────────────────────────────────────────────────
    "sc_open_images":   "   Ctrl+O",
    "sc_paste":         "   Ctrl+V",
    "sc_save_txt":      "   Ctrl+S",
    "sc_copy_all":      "   Ctrl+Shift+C",

    # ── Durum çubuğu ──────────────────────────────────────────────────────────
    "status_ready":     "Hazır",
    "status_copied":    "Panoya kopyalandı.",
    "status_qr_copied": "QR kod panoya kopyalandı.",
    "status_checking":  "Güncellemeler kontrol ediliyor…",
    "status_upgrading": "Güncelleniyor… lütfen bekleyin.",
    "status_sources":   "{sources} kaynak  ·  {qrs} QR kod çözüldü",

    # ── Çıktı alanı ───────────────────────────────────────────────────────────
    "placeholder_output":  "QR sonucu burada görünecek…",
    "result_no_qr":        "QR kod bulunamadı.",

    # ── Mesajlar ──────────────────────────────────────────────────────────────
    "msg_no_image_clipboard":   "Panoda resim yok.",
    "msg_no_content_save":      "Kaydedilecek içerik yok.",
    "msg_no_content_copy":      "Kopyalanacak içerik yok.",
    "msg_no_history":           "Bu oturumda henüz geçmiş yok.",
    "msg_no_images_folder":     "Klasörde resim dosyası bulunamadı.",
    "msg_file_saved":           "Dosya kaydedildi.",
    "msg_csv_saved":            "CSV kaydedildi.",
    "msg_json_saved":           "JSON kaydedildi.",
    "msg_qr_saved":             "QR kod kaydedildi.",
    "msg_generate_first":       "Önce bir QR kod oluşturun.",
    "msg_enter_text":           "Lütfen bir metin veya URL girin.",
    "msg_upgrade_success":      "Güncelleme başarılı! Uygulama şimdi yeniden başlayacak.",
    "msg_update_timeout":       "Güncelleme kontrolü zaman aşımına uğradı. Lütfen tekrar deneyin.",
    "msg_restart_language":     "Yeni dil için uygulamayı yeniden başlatın.",

    # ── Güncelleme ────────────────────────────────────────────────────────────
    "upd_up_to_date":       "En güncel sürümü kullanıyorsunuz (v{version}).",
    "upd_already_latest":   "Zaten en güncel sürümdesiniz (v{version}).",
    "upd_available":        "Yeni sürüm v{version} mevcut.\nİndirmek için github.com/NmnRn/QR-to-TXT adresini ziyaret edin.",
    "upd_upgrade_prompt":   "Daha yeni bir sürüm mevcut (şu an v{version}).\nŞimdi güncellensin mi?\n\nGüncelleme sonrası uygulama yeniden başlayacak.",
    "upd_reach_remote":     "Uzak sunucuya erişilemedi:\n{error}",
    "upd_reach_server":     "Güncelleme sunucusuna erişilemedi:\n{error}",

    # ── Diyalog başlıkları ────────────────────────────────────────────────────
    "dlg_open_images":      "QR resim(ler)i seçin",
    "dlg_open_folder":      "Klasör seçin",
    "dlg_open_pdf":         "PDF seçin",
    "dlg_save_txt":         "TXT Olarak Kaydet",
    "dlg_save_csv":         "CSV Olarak Kaydet",
    "dlg_save_json":        "JSON Olarak Kaydet",
    "dlg_save_qr":          "QR Kodu Kaydet",
    "dlg_history_title":    "Oturum Geçmişi",
    "dlg_history_hint":     "Tam sonuçları görmek için bir girdiye tıklayın:",
    "dlg_settings_title":   "Ayarlar",
    "dlg_generator_title":  "QR Kod Oluştur",
    "dlg_version_text":     "QR to TXT\nSürüm: v{version}",

    # ── Ayarlar etiketleri ────────────────────────────────────────────────────
    "settings_theme":           "Tema:",
    "settings_language":        "Dil:",
    "settings_save_folder":     "Varsayılan kayıt klasörü:",
    "settings_history_limit":   "Geçmiş limiti (kayıt):",
    "settings_check_updates":   "Başlangıçta güncelleme kontrol et:",

    # ── Oluşturucu diyalog ────────────────────────────────────────────────────
    "gen_hint":         "Kodlamak için metin veya URL girin",
    "gen_placeholder":  "Bir link yapıştırın veya metin yazın…",
    "gen_type_none":    "—",
    "gen_type_link":    "Link",
    "gen_type_text":    "Metin",
    "gen_generate":     "Oluştur  →",
    "gen_save_png":     "PNG Kaydet",
    "gen_copy_image":   "Resmi Kopyala",
    "gen_qr_placeholder": "QR kod burada görünecek",
    "gen_auto_saved":   "QR Codes/ klasörüne otomatik kaydedildi",

    # ── Geçmiş diyalogu ───────────────────────────────────────────────────────
    "hist_source":      "Kaynak:    {source}",
    "hist_time":        "Zaman:     {time}",
    "hist_no_qr":       "(QR yok)",
    "hist_no_qr_found": "QR kod bulunamadı.",

    # ── Sistem tepsisi ────────────────────────────────────────────────────────
    "tray_show":    "Göster",
    "tray_quit":    "Çıkış",
    "tray_tooltip": "QR to TXT",

    # ── Hatalar ───────────────────────────────────────────────────────────────
    "err_upgrade_failed":   "Güncelleme başarısız",
    "err_missing_pdf":      "PDF desteği pymupdf gerektirir:\n\npip install pymupdf",
    "err_missing_qrcode":   "QR oluşturma qrcode gerektirir:\n\npip install \"qrcode[pil]\"",

    # ── Mesaj kutusu başlıkları ───────────────────────────────────────────────
    "title_info":           "Bilgi",
    "title_error":          "Hata",
    "title_errors":         "Hatalar",
    "title_saved":          "Kaydedildi",
    "title_upgrade":        "Güncelle",
    "title_up_to_date":     "Güncel",
    "title_upgrade_avail":  "Güncelleme mevcut",
    "title_upgrade_fail":   "Güncelleme başarısız",
    "title_upgrade_ok":     "Güncelleme tamamlandı",
    "title_update_check":   "Güncelleme kontrolü",
    "title_update_fail":    "Güncelleme kontrolü başarısız",
    "title_update_avail":   "Güncelleme mevcut",
    "title_missing_pkg":    "Eksik paket",
    "title_version":        "Sürüm",
    "title_language":       "Dil",
}
