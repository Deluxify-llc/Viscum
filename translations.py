"""
Complete internationalization for Viscum GUI

Auto-detects user's system language and provides translations for ALL UI elements.
"""

import locale

SUPPORTED_LANGUAGES = ['en', 'es', 'zh', 'hi', 'fr', 'de']

def get_system_language():
    """Detect system language from locale"""
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            lang_code = system_locale.split('_')[0].lower()
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
    except:
        pass
    return 'en'

# Complete translation dictionaries
TRANSLATIONS = {
    'en': {  # English - COMPLETE
        # Window
        'window_title': 'Viscum - Ball Tracker for Viscosity Measurement',

        # Tabs
        'tab_main': 'Main',
        'tab_setup': 'Setup & Configuration',
        'tab_preview': 'Preview & Navigation',
        'tab_results': 'Results & Messages',

        # Sections
        'section_video': '1. Video Selection',
        'section_roi': '2. ROI Selection',
        'section_frames': '3. Frame Range',
        'section_ball': '4. Ball Properties',
        'section_liquid': '5. Liquid Properties',
        'section_calibration': '6. Calibration (Optional)',
        'section_preview': 'Preview',
        'section_calculated': 'Calculated Values',
        'section_calib_results': 'Calibration Results',
        'section_graphs': 'Graphs',
        'section_full_output': 'Full Output',

        # Buttons
        'btn_browse': 'Browse Video',
        'btn_select_roi': 'Select ROI on Video',
        'btn_preview': 'Preview Frame',
        'btn_run': 'Run Tracking',
        'btn_close': 'Close',
        'btn_save_results': 'Save Results',

        # Labels
        'lbl_x1': 'X1:',
        'lbl_y1': 'Y1:',
        'lbl_x2': 'X2:',
        'lbl_y2': 'Y2:',
        'lbl_start_frame': 'Start Frame:',
        'lbl_end_frame': 'End Frame:',
        'lbl_diameter': 'Diameter (mm):',
        'lbl_ball_density': 'Density (kg/m³):',
        'lbl_liquid_density': 'Density (kg/m³):',
        'lbl_gravity': 'Gravity (m/s²):',
        'lbl_temperature': 'Temperature (°C):',
        'lbl_visc_40': 'Viscosity @ 40°C (cP):',
        'lbl_visc_100': 'Viscosity @ 100°C (cP):',
        'lbl_frame': 'Frame: {current}/{total}',

        # Checkboxes
        'chk_calibration': 'This is a calibration test',

        # Status messages
        'status_ready': 'Ready',
        'status_no_video': 'No video loaded',
        'status_video_loaded': 'FPS: {fps:.1f} | Frames: {frames}',
        'status_roi_select': 'Click and drag to select ROI',
        'status_roi_selected': 'ROI selected',
        'status_running': 'Running tracking...',
        'status_complete': 'Tracking complete!',
        'status_error': 'Error occurred',

        # UI hints
        'roi_hint': 'Click and drag on video to select ROI',
        'results_placeholder': 'Results will appear here after tracking completes',

        # Results window
        'results_title': 'Tracking Results',
        'results_header': 'Viscosity Measurement Results',
        'result_avg_diameter': 'Average Ball Diameter:',
        'result_velocity_px': 'Final Velocity (pixels/s):',
        'result_mm_per_px': 'Pixel to mm Conversion:',
        'result_velocity_mm': 'Velocity (mm/s):',
        'result_viscosity': 'MEASURED VISCOSITY:',
        'result_activation_energy': 'Activation Energy:',
        'result_pre_exp': 'Pre-exponential Factor:',
        'result_expected_visc': 'Expected Viscosity:',
        'result_error': 'RELATIVE ERROR:',
        'result_no_parse': 'Could not parse results. See full output below.',

        # Confidence explanation
        'help_confidence': 'About Confidence Scores',
        'confidence_title': 'Understanding Confidence Scores',
        'confidence_intro': 'Confidence indicates how certain the tracking algorithm is about ball detection in each frame.',
        'confidence_high': '• Green (>0.7): High confidence - Ball clearly detected',
        'confidence_medium': '• Yellow (0.4-0.7): Medium confidence - Detection approximate',
        'confidence_low': '• Red (<0.4): Low confidence - Using prediction',
        'confidence_avg': 'Average confidence should be >0.6 for reliable results.',
        'confidence_note': 'Low confidence frames use Kalman filter prediction based on previous positions.',

        # Dialog titles
        'dialog_select_video': 'Select Video File',
        'dialog_video_files': 'Video files',
        'dialog_all_files': 'All files',

        # Warning/Error messages
        'warn_title': 'Warning',
        'warn_no_video': 'Please load a video first',
        'warn_select_video': 'Please select a video file',
        'error_title': 'Error',
        'error_open_video': 'Could not open video file',
        'error_tracking_failed': 'Tracking failed:\n{error}',

        # Tooltips
        'tooltip_browse': 'Select a video file (.mp4, .avi, .mov, .mkv) showing a ball falling through fluid',
        'tooltip_roi_x1': 'Left edge of the Region of Interest in pixels (top-left corner x-coordinate)',
        'tooltip_roi_y1': 'Top edge of the Region of Interest in pixels (top-left corner y-coordinate)',
        'tooltip_roi_x2': 'Right edge of the Region of Interest in pixels (bottom-right corner x-coordinate)',
        'tooltip_roi_y2': 'Bottom edge of the Region of Interest in pixels (bottom-right corner y-coordinate)',
        'tooltip_select_roi': 'Click this button, then click and drag on the video to select the rectangular area where the ball falls',
        'tooltip_start_frame': 'Frame number where the ball enters the ROI. Ball should be at terminal velocity (constant speed) by this point.',
        'tooltip_end_frame': 'Frame number where the ball exits the ROI or before it hits the bottom',
        'tooltip_preview': 'Jump to the start frame to verify the ROI and frame range are correct',
        'tooltip_diameter': 'Real-world diameter of the ball in millimeters. Measure accurately with calipers. Example: 3.0 mm',
        'tooltip_ball_density': 'Density of ball material in kg/m³. Common values: Steel ≈ 7850, Glass ≈ 2500, Plastic/Acrylic ≈ 880',
        'tooltip_liquid_density': 'Density of the liquid in kg/m³. Common values: Water ≈ 1000, Mineral Oil ≈ 870, Glycerin ≈ 1260',
        'tooltip_gravity': 'Local gravitational acceleration in m/s². Typically 9.79-9.82 depending on latitude and elevation. Use 9.79 for sea level mid-latitudes.',
        'tooltip_calibration': 'Check this if you are testing with a fluid of known viscosity to validate measurement accuracy',
        'tooltip_temperature': 'Temperature of the liquid during the test in degrees Celsius. Temperature significantly affects viscosity.',
        'tooltip_visc_40': 'Manufacturer-specified viscosity at 40°C in centipoise (cP). Found in fluid datasheet. Used for calibration validation.',
        'tooltip_visc_100': 'Manufacturer-specified viscosity at 100°C in centipoise (cP). Found in fluid datasheet. Used for Arrhenius equation.',
        'tooltip_run': 'Start the ball tracking algorithm and calculate viscosity using Stokes\' Law. This may take a few minutes.',
        'tooltip_nav_backward_fast': 'Jump backward 10 frames in the video',
        'tooltip_nav_backward': 'Go to previous frame',
        'tooltip_nav_forward': 'Go to next frame',
        'tooltip_nav_forward_fast': 'Jump forward 10 frames in the video',
        'tooltip_frame_slider': 'Drag to navigate to any frame in the video',
    },

    'es': {  # Spanish - COMPLETE
        # Window
        'window_title': 'Viscum - Rastreador de Bolas para Medición de Viscosidad',

        # Tabs
        'tab_main': 'Principal',
        'tab_setup': 'Configuración',
        'tab_preview': 'Vista Previa y Navegación',
        'tab_results': 'Resultados y Mensajes',

        # Sections
        'section_video': '1. Selección de Video',
        'section_roi': '2. Selección de ROI',
        'section_frames': '3. Rango de Fotogramas',
        'section_ball': '4. Propiedades de la Bola',
        'section_liquid': '5. Propiedades del Líquido',
        'section_calibration': '6. Calibración (Opcional)',
        'section_preview': 'Vista Previa',
        'section_calculated': 'Valores Calculados',
        'section_calib_results': 'Resultados de Calibración',
        'section_graphs': 'Gráficos',
        'section_full_output': 'Salida Completa',

        # Buttons
        'btn_browse': 'Examinar Video',
        'btn_select_roi': 'Seleccionar ROI en Video',
        'btn_preview': 'Vista Previa de Fotograma',
        'btn_run': 'Ejecutar Rastreo',
        'btn_close': 'Cerrar',
        'btn_save_results': 'Guardar Resultados',

        # Labels
        'lbl_x1': 'X1:',
        'lbl_y1': 'Y1:',
        'lbl_x2': 'X2:',
        'lbl_y2': 'Y2:',
        'lbl_start_frame': 'Fotograma Inicial:',
        'lbl_end_frame': 'Fotograma Final:',
        'lbl_diameter': 'Diámetro (mm):',
        'lbl_ball_density': 'Densidad (kg/m³):',
        'lbl_liquid_density': 'Densidad (kg/m³):',
        'lbl_gravity': 'Gravedad (m/s²):',
        'lbl_temperature': 'Temperatura (°C):',
        'lbl_visc_40': 'Viscosidad @ 40°C (cP):',
        'lbl_visc_100': 'Viscosidad @ 100°C (cP):',
        'lbl_frame': 'Fotograma: {current}/{total}',

        # Checkboxes
        'chk_calibration': 'Esta es una prueba de calibración',

        # Status messages
        'status_ready': 'Listo',
        'status_no_video': 'No hay video cargado',
        'status_video_loaded': 'FPS: {fps:.1f} | Fotogramas: {frames}',
        'status_roi_select': 'Haga clic y arrastre para seleccionar ROI',
        'status_roi_selected': 'ROI seleccionado',
        'status_running': 'Ejecutando rastreo...',
        'status_complete': '¡Rastreo completo!',
        'status_error': 'Ocurrió un error',

        # UI hints
        'roi_hint': 'Haga clic y arrastre en el video para seleccionar ROI',
        'results_placeholder': 'Los resultados aparecerán aquí después de completar el rastreo',

        # Results window
        'results_title': 'Resultados del Rastreo',
        'results_header': 'Resultados de Medición de Viscosidad',
        'result_avg_diameter': 'Diámetro Promedio de la Bola:',
        'result_velocity_px': 'Velocidad Final (píxeles/s):',
        'result_mm_per_px': 'Conversión de Píxel a mm:',
        'result_velocity_mm': 'Velocidad (mm/s):',
        'result_viscosity': 'VISCOSIDAD MEDIDA:',
        'result_activation_energy': 'Energía de Activación:',
        'result_pre_exp': 'Factor Pre-exponencial:',
        'result_expected_visc': 'Viscosidad Esperada:',
        'result_error': 'ERROR RELATIVO:',
        'result_no_parse': 'No se pudieron analizar los resultados. Vea la salida completa a continuación.',

        # Confidence explanation
        'help_confidence': 'Acerca de las Puntuaciones de Confianza',
        'confidence_title': 'Entendiendo las Puntuaciones de Confianza',
        'confidence_intro': 'La confianza indica qué tan seguro está el algoritmo de rastreo sobre la detección de la bola en cada fotograma.',
        'confidence_high': '• Verde (>0.7): Alta confianza - Bola claramente detectada',
        'confidence_medium': '• Amarillo (0.4-0.7): Confianza media - Detección aproximada',
        'confidence_low': '• Rojo (<0.4): Baja confianza - Usando predicción',
        'confidence_avg': 'La confianza promedio debe ser >0.6 para resultados confiables.',
        'confidence_note': 'Los fotogramas de baja confianza usan predicción del filtro de Kalman basada en posiciones anteriores.',

        # Dialog titles
        'dialog_select_video': 'Seleccionar Archivo de Video',
        'dialog_video_files': 'Archivos de video',
        'dialog_all_files': 'Todos los archivos',

        # Warning/Error messages
        'warn_title': 'Advertencia',
        'warn_no_video': 'Por favor, cargue un video primero',
        'warn_select_video': 'Por favor, seleccione un archivo de video',
        'error_title': 'Error',
        'error_open_video': 'No se pudo abrir el archivo de video',
        'error_tracking_failed': 'El rastreo falló:\n{error}',

        # Tooltips
        'tooltip_browse': 'Seleccione un archivo de video (.mp4, .avi, .mov, .mkv) mostrando una bola cayendo a través del fluido',
        'tooltip_roi_x1': 'Borde izquierdo de la Región de Interés en píxeles (coordenada x de la esquina superior izquierda)',
        'tooltip_roi_y1': 'Borde superior de la Región de Interés en píxeles (coordenada y de la esquina superior izquierda)',
        'tooltip_roi_x2': 'Borde derecho de la Región de Interés en píxeles (coordenada x de la esquina inferior derecha)',
        'tooltip_roi_y2': 'Borde inferior de la Región de Interés en píxeles (coordenada y de la esquina inferior derecha)',
        'tooltip_select_roi': 'Haga clic en este botón, luego haga clic y arrastre en el video para seleccionar el área rectangular donde cae la bola',
        'tooltip_start_frame': 'Número de fotograma donde la bola entra en el ROI. La bola debe estar a velocidad terminal (velocidad constante) en este punto.',
        'tooltip_end_frame': 'Número de fotograma donde la bola sale del ROI o antes de que toque el fondo',
        'tooltip_preview': 'Saltar al fotograma inicial para verificar que el ROI y el rango de fotogramas sean correctos',
        'tooltip_diameter': 'Diámetro real de la bola en milímetros. Mida con precisión con calibradores. Ejemplo: 3.0 mm',
        'tooltip_ball_density': 'Densidad del material de la bola en kg/m³. Valores comunes: Acero ≈ 7850, Vidrio ≈ 2500, Plástico/Acrílico ≈ 880',
        'tooltip_liquid_density': 'Densidad del líquido en kg/m³. Valores comunes: Agua ≈ 1000, Aceite mineral ≈ 870, Glicerina ≈ 1260',
        'tooltip_gravity': 'Aceleración gravitacional local en m/s². Típicamente 9.79-9.82 dependiendo de la latitud y elevación. Use 9.79 para latitudes medias al nivel del mar.',
        'tooltip_calibration': 'Marque esto si está probando con un fluido de viscosidad conocida para validar la precisión de la medición',
        'tooltip_temperature': 'Temperatura del líquido durante la prueba en grados Celsius. La temperatura afecta significativamente la viscosidad.',
        'tooltip_visc_40': 'Viscosidad especificada por el fabricante a 40°C en centipoise (cP). Se encuentra en la hoja de datos del fluido. Se usa para validación de calibración.',
        'tooltip_visc_100': 'Viscosidad especificada por el fabricante a 100°C en centipoise (cP). Se encuentra en la hoja de datos del fluido. Se usa para la ecuación de Arrhenius.',
        'tooltip_run': 'Inicie el algoritmo de rastreo de bola y calcule la viscosidad usando la Ley de Stokes. Esto puede tardar unos minutos.',
        'tooltip_nav_backward_fast': 'Retroceder 10 fotogramas en el video',
        'tooltip_nav_backward': 'Ir al fotograma anterior',
        'tooltip_nav_forward': 'Ir al siguiente fotograma',
        'tooltip_nav_forward_fast': 'Avanzar 10 fotogramas en el video',
        'tooltip_frame_slider': 'Arrastre para navegar a cualquier fotograma en el video',
    },

    'zh': {  # Chinese
        'window_title': 'Viscum - 粘度测量球追踪器',
        'section_video': '1. 视频选择',
        'section_roi': '2. ROI选择',
        'section_ball': '4. 球属性',
        'btn_browse': '浏览视频',
        'btn_run': '运行追踪',
        'status_no_video': '未加载视频',
    },

    'hi': {  # Hindi
        'window_title': 'Viscum - विस्कोसिटी माप के लिए बॉल ट्रैकर',
        'section_video': '1. वीडियो चयन',
        'btn_browse': 'वीडियो ब्राउज़ करें',
        'status_no_video': 'कोई वीडियो लोड नहीं',
    },

    'fr': {  # French
        'window_title': 'Viscum - Suivi de Balle pour Mesure de Viscosité',
        'section_video': '1. Sélection Vidéo',
        'btn_browse': 'Parcourir Vidéo',
        'status_no_video': 'Aucune vidéo chargée',
    },

    'de': {  # German
        'window_title': 'Viscum - Ballverfolger für Viskositätsmessung',
        'section_video': '1. Videoauswahl',
        'btn_browse': 'Video durchsuchen',
        'status_no_video': 'Kein Video geladen',
    },
}


class Translator:
    """Helper class for translations with fallback to English"""

    def __init__(self, language=None):
        if language is None:
            language = get_system_language()
        self.language = language
        self.translations = TRANSLATIONS.get(language, TRANSLATIONS['en'])
        self.fallback = TRANSLATIONS['en']

    def get(self, key, **kwargs):
        """Get translation for key, with fallback to English"""
        text = self.translations.get(key, self.fallback.get(key, key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        return text

    def __getitem__(self, key):
        """Allow dictionary-style access"""
        return self.get(key)


# Global translator
_translator = Translator()

def get_text(key, **kwargs):
    """Get translated text"""
    return _translator.get(key, **kwargs)

def set_language(language):
    """Change language"""
    global _translator
    _translator = Translator(language)

def get_current_language():
    """Get current language code"""
    return _translator.language
