# en bienes_app/pdf_generator.py

from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
import os

def generar_reporte_inventario_pdf(bienes_queryset, fecha_desde, fecha_hasta, titulo_reporte="INVENTARIO GENERAL DE BIENES PÚBLICOS"):
    # 1. Preparar el buffer de respuesta HTTP para el PDF
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

    elementos = []
    styles = getSampleStyleSheet()

    # 3. Lógica del Encabezado (Membrete y Logo)
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo_ipsfa.png')
    logo = None
    if os.path.exists(logo_path):
        logo = logo_path  # Guardamos la ruta para usarla en el canvas

    membrete_text = (
        'REPÚBLICA BOLIVARIANA DE VENEZUELA<br/>'
        'MINISTERIO DEL PODER POPULAR PARA LA DEFENSA<br/>'
        'VICEMINISTERIO DE SERVICIOS, PERSONAL Y LOGÍSTICA<br/>'
        'DIRECCIÓN GENERAL DE  EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    # Agregamos el membrete centrado
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.3*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.9*inch, width=0.7*inch, height=0.9*inch, mask='auto')

    # 4. Título del Reporte
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1 # 1 = CENTER
    elementos.append(titulo)

    # Rango de fechas
    rango_fechas = Paragraph(f"Desde: {fecha_desde} Hasta: {fecha_hasta}", styles['Normal'])
    rango_fechas.style.alignment = 1 # 1 = CENTER
    elementos.append(rango_fechas)
    elementos.append(Spacer(1, 0.3*inch))

    # 5. Lógica de la Tabla de Datos
    columnas = ['N°', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'MARCA', 'MODELO', 'SERIAL', 'UNIDAD ASIGNADA']
    # Estilo para celdas de la tabla
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 8
    cell_style.leading = 9
    cell_style.wordWrap = 'LTR'  # Ajuste de línea por palabra
    # Estilo para encabezados de la tabla
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 8
    header_style.leading = 9
    header_style.wordWrap = 'LTR'  # Ajuste de línea por palabra
    header_style.alignment = 1  # Centrado
    # Convertir los títulos de columna en Paragraph con color blanco y negrita
    columnas_paragraph = [
        Paragraph(f'<font color="white"><b>{col}</b></font>', header_style) for col in columnas
    ]
    datos_tabla = [columnas_paragraph]
    for i, bien in enumerate(bienes_queryset):
        unidad_nombre = bien.unidad_administrativa_actual.nombre if bien.unidad_administrativa_actual else 'N/A'
        datos_tabla.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(str(bien.codigo_patrimonial), cell_style),
            Paragraph(str(bien.descripcion), cell_style),
            Paragraph(str(bien.marca or ''), cell_style),
            Paragraph(str(bien.modelo or ''), cell_style),
            Paragraph(str(bien.serial or ''), cell_style),
            Paragraph(str(unidad_nombre), cell_style),
        ])

    # Ajustar los anchos de columna para respetar márgenes y reducir "DESCRIPCIÓN"
    tabla_bienes = Table(
        datos_tabla,
        colWidths=[0.4*inch, 0.9*inch, 1.2*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.8*inch]
    )
    tabla_bienes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('ROWHEIGHT', (0, 1), (-1, -1), 20),
    ]))
    elementos.append(tabla_bienes)
    elementos.append(Spacer(1, 0.5*inch))

    # 6. Lógica del Pie de Página (Firma)
    elementos.append(Spacer(1, 2*inch))

    linea_firma = "____________________________________"
    nombre_firmante = "MY. ANDELSON JOSE PINTO HERRERA"
    cargo_firmante = "JEFE DEL DEPARTAMENTO BIENES PÚBLICOS"

    p_linea = Paragraph(linea_firma, styles['Normal'])
    p_linea.style.alignment = 1
    p_nombre = Paragraph(nombre_firmante, styles['Normal'])
    p_nombre.style.alignment = 1
    p_cargo = Paragraph(cargo_firmante, styles['Normal'])
    p_cargo.style.alignment = 1

    elementos.append(p_linea)
    elementos.append(p_nombre)
    elementos.append(p_cargo)

    # Construir el PDF
    doc.build(elementos, onFirstPage=draw_logo)

    # 7. Devolver el buffer con el PDF generado
    buffer.seek(0)
    return buffer

def generar_reporte_desincorporados_pdf(movimientos_queryset, fecha_desde, fecha_hasta, titulo_reporte):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elementos = []
    styles = getSampleStyleSheet()

    # Encabezado (Membrete y Logo)
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo_ipsfa.png')
    logo = None
    if os.path.exists(logo_path):
        logo = logo_path
    membrete_text = (
        'REPÚBLICA BOLIVARIANA DE VENEZUELA<br/>'
        'MINISTERIO DEL PODER POPULAR PARA LA DEFENSA<br/>'
        'VICEMINISTERIO DE SERVICIOS, PERSONAL Y LOGÍSTICA<br/>'
        'DIRECCIÓN GENERAL DE  EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.3*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.9*inch, width=0.7*inch, height=0.9*inch, mask='auto')

    # Título del Reporte
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1 # CENTER
    elementos.append(titulo)

    # Rango de fechas
    rango_fechas = Paragraph(f"Desde: {fecha_desde} Hasta: {fecha_hasta}", styles['Normal'])
    rango_fechas.style.alignment = 1
    elementos.append(rango_fechas)
    elementos.append(Spacer(1, 0.3*inch))

    # Lógica de la Tabla de Datos
    columnas = ['N°', 'FECHA DESINC.', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'SERIAL', 'MOTIVO']
    # Estilo para celdas de la tabla
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 8
    cell_style.leading = 9
    cell_style.wordWrap = 'LTR'  # Ajuste de línea por palabra
    # Estilo para encabezados de la tabla
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 8
    header_style.leading = 9
    header_style.wordWrap = 'LTR'  # Ajuste de línea por palabra
    header_style.alignment = 1  # Centrado
    # Convertir los títulos de columna en Paragraph con color blanco y negrita
    columnas_paragraph = [
        Paragraph(f'<font color="white"><b>{col}</b></font>', header_style) for col in columnas
    ]
    datos_tabla = [columnas_paragraph]
    for i, movimiento in enumerate(movimientos_queryset):
        datos_tabla.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(movimiento.fecha_movimiento.strftime('%d/%m/%Y'), cell_style),
            Paragraph(str(movimiento.bien.codigo_patrimonial), cell_style),
            Paragraph(str(movimiento.bien.descripcion), cell_style),
            Paragraph(str(movimiento.bien.serial or ''), cell_style),
            Paragraph(str(movimiento.motivo_desincorporacion or ''), cell_style),
        ])
    tabla_reporte = Table(
        datos_tabla,
        colWidths=[0.4*inch, 1*inch, 1.2*inch, 1.8*inch, 1*inch, 1.2*inch, 1.2*inch]
    )
    tabla_reporte.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('ROWHEIGHT', (0, 1), (-1, -1), 20),
    ]))
    elementos.append(tabla_reporte)
    elementos.append(Spacer(1, 0.5*inch))

    # Pie de página (Firma)
    elementos.append(Spacer(1, 2*inch))
    linea_firma = "____________________________________"
    nombre_firmante = "MY. ANDELSON JOSE PINTO HERRERA"
    cargo_firmante = "JEFE DEL DEPARTAMENTO DE BIENES PÚBLICOS"
    p_linea = Paragraph(linea_firma, styles['Normal'])
    p_linea.style.alignment = 1
    p_nombre = Paragraph(nombre_firmante, styles['Normal'])
    p_nombre.style.alignment = 1
    p_cargo = Paragraph(cargo_firmante, styles['Normal'])
    p_cargo.style.alignment = 1
    elementos.append(p_linea)
    elementos.append(p_nombre)
    elementos.append(p_cargo)

    doc.build(elementos, onFirstPage=draw_logo)
    buffer.seek(0)
    return buffer

def generar_reporte_traslados_pdf(movimientos_queryset, fecha_desde, fecha_hasta, titulo_reporte):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elementos = []
    styles = getSampleStyleSheet()

    # Encabezado (Membrete y Logo)
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo_ipsfa.png')
    logo = None
    if os.path.exists(logo_path):
        logo = logo_path
    membrete_text = (
        'REPÚBLICA BOLIVARIANA DE VENEZUELA<br/>'
        'MINISTERIO DEL PODER POPULAR PARA LA DEFENSA<br/>'
        'VICEMINISTERIO DE SERVICIOS, PERSONAL Y LOGÍSTICA<br/>'
        'DIRECCIÓN GENERAL DE  EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.3*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.1*inch, width=0.7*inch, height=0.9*inch, mask='auto')

    # Título y Rango de Fechas
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)
    rango_fechas = Paragraph(f"Período: Desde {fecha_desde} Hasta {fecha_hasta}", styles['Normal'])
    rango_fechas.style.alignment = 1
    elementos.append(rango_fechas)
    elementos.append(Spacer(1, 0.3*inch))

    # Tabla de Datos
    columnas = ['N°', 'FECHA', 'CÓDIGO BNM', 'DESCRIPCIÓN', 'UNIDAD ORIGEN', 'UNIDAD DESTINO', 'NUEVO RESPONSABLE', 'N° OFICIO']
    # Estilo para celdas de la tabla
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 8
    cell_style.leading = 9
    cell_style.wordWrap = 'LTR'
    # Estilo para encabezados de la tabla
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 8
    header_style.leading = 9
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    # Convertir los títulos de columna en Paragraph con color blanco y negrita
    columnas_paragraph = [
        Paragraph(f'<font color="white"><b>{col}</b></font>', header_style) for col in columnas
    ]
    datos_tabla = [columnas_paragraph]
    for i, movimiento in enumerate(movimientos_queryset):
        datos_tabla.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(movimiento.fecha_movimiento.strftime('%d/%m/%Y'), cell_style),
            Paragraph(str(movimiento.bien.codigo_patrimonial), cell_style),
            Paragraph(str(movimiento.bien.descripcion), cell_style),
            Paragraph(str(movimiento.unidad_origen.nombre if movimiento.unidad_origen else 'N/A'), cell_style),
            Paragraph(str(movimiento.unidad_destino.nombre if movimiento.unidad_destino else 'N/A'), cell_style),
            Paragraph(str(movimiento.responsable_nuevo_nombre or ''), cell_style),
            Paragraph(str(movimiento.numero_oficio_referencia or ''), cell_style)
        ])

    tabla_reporte = Table(datos_tabla, colWidths=[0.4*inch, 0.9*inch, 1*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.6*inch])
    tabla_reporte.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    elementos.append(tabla_reporte)

    # Pie de página (Firma)
    elementos.append(Spacer(1, 0.5*inch))
    linea_firma = "____________________________________"
    nombre_firmante = "MY. ANDELSON JOSE PINTO HERRERA"
    cargo_firmante = "JEFE DEL DEPARTAMENTO DE BIENES PÚBLICOS"
    p_linea = Paragraph(linea_firma, styles['Normal'])
    p_linea.style.alignment = 1
    p_nombre = Paragraph(nombre_firmante, styles['Normal'])
    p_nombre.style.alignment = 1
    p_cargo = Paragraph(cargo_firmante, styles['Normal'])
    p_cargo.style.alignment = 1
    elementos.append(p_linea)
    elementos.append(p_nombre)
    elementos.append(p_cargo)

    doc.build(elementos, onFirstPage=draw_logo)
    buffer.seek(0)
    return buffer

# --- NUEVA FUNCIÓN PARA REPORTE DE DEPRECIACIÓN ---
def generar_reporte_depreciacion_pdf(bienes_con_depreciacion, fecha_hasta, titulo_reporte):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elementos = []
    styles = getSampleStyleSheet()

    # Encabezado (logo y membrete)
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo_ipsfa.png')
    logo = None
    if os.path.exists(logo_path):
        logo = logo_path
    membrete_text = (
        'REPÚBLICA BOLIVARIANA DE VENEZUELA<br/>'
        'MINISTERIO DEL PODER POPULAR PARA LA DEFENSA<br/>'
        'VICEMINISTERIO DE SERVICIOS, PERSONAL Y LOGÍSTICA<br/>'
        'DIRECCIÓN GENERAL DE EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.3*inch))
    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.9*inch, width=0.7*inch, height=0.9*inch, mask='auto')
    # Título y Fecha
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)
    fecha_corte = Paragraph(f"Cálculos hasta la fecha: {fecha_hasta}", styles['Normal'])
    fecha_corte.style.alignment = 1
    elementos.append(fecha_corte)
    elementos.append(Spacer(1, 0.3*inch))
    # Tabla de Datos
    columnas = ['N°', 'CÓDIGO BNM', 'DESCRIPCIÓN', 'VALOR ORIGINAL (Bs.)', 'DEPRECIACIÓN ACUMULADA (Bs.)', 'VALOR NETO EN LIBROS (Bs.)']
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 8
    cell_style.leading = 9
    cell_style.wordWrap = 'LTR'
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 8
    header_style.leading = 9
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    columnas_paragraph = [Paragraph(f'<font color="white"><b>{col}</b></font>', header_style) for col in columnas]
    datos_tabla = [columnas_paragraph]
    for i, bien in enumerate(bienes_con_depreciacion):
        datos_tabla.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(str(bien.codigo_patrimonial), cell_style),
            Paragraph(str(bien.descripcion), cell_style),
            Paragraph(f"{bien.valor_unitario_bs:,.2f}", cell_style),
            Paragraph(f"{bien.ultima_depreciacion_acumulada or 0:,.2f}", cell_style),
            Paragraph(f"{bien.ultimo_valor_neto or bien.valor_unitario_bs:,.2f}", cell_style)
        ])
    tabla_reporte = Table(datos_tabla, colWidths=[0.4*inch, 1*inch, 2.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    tabla_reporte.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('ROWHEIGHT', (0, 1), (-1, -1), 20),
    ]))
    elementos.append(tabla_reporte)
    elementos.append(Spacer(1, 0.5*inch))
    # Pie de página (Firma)
    elementos.append(Spacer(1, 2*inch))
    linea_firma = "____________________________________"
    nombre_firmante = "MY. ANDELSON JOSE PINTO HERRERA"
    cargo_firmante = "JEFE DEL DEPARTAMENTO DE BIENES PÚBLICOS"
    p_linea = Paragraph(linea_firma, styles['Normal'])
    p_linea.style.alignment = 1
    p_nombre = Paragraph(nombre_firmante, styles['Normal'])
    p_nombre.style.alignment = 1
    p_cargo = Paragraph(cargo_firmante, styles['Normal'])
    p_cargo.style.alignment = 1
    elementos.append(p_linea)
    elementos.append(p_nombre)
    elementos.append(p_cargo)
    doc.build(elementos, onFirstPage=draw_logo)
    buffer.seek(0)
    return buffer