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
from django.utils import timezone

def draw_watermark(canvas, doc):
    """Función para dibujar la marca de agua con el logo de IPSFANB"""
    try:
        # Ruta del logo de IPSFANB (el logo circular que viste)
        logo_path = os.path.join(settings.BASE_DIR, 'static/images/watermark.png')
        
        if os.path.exists(logo_path):
            # Obtener dimensiones del documento
            page_width = doc.pagesize[0]
            page_height = doc.pagesize[1]
            
            # Calcular posición centrada para la marca de agua
            watermark_width = 4 * inch  # Aumentado de 2.5 a 4 pulgadas
            watermark_height = 4 * inch  # Aumentado de 2.5 a 4 pulgadas
            x = (page_width - watermark_width) / 2
            y = (page_height - watermark_height) / 2
            
            # Dibujar la marca de agua con transparencia
            canvas.saveState()
            canvas.setFillAlpha(0.08)  # Transparencia del 8% para que sea sutil
            canvas.drawImage(logo_path, x, y, width=watermark_width, height=watermark_height, mask='auto')
            canvas.restoreState()
    except Exception as e:
        # Si hay error al cargar la marca de agua, continuar sin ella
        print(f"Error al cargar marca de agua: {e}")

def generar_reporte_inventario_pdf(bienes_queryset, fecha_desde, fecha_hasta, titulo_reporte="INVENTARIO GENERAL DE BIENES PÚBLICOS"):
    # 1. Preparar el buffer de respuesta HTTP para el PDF
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)

    elementos = []
    styles = getSampleStyleSheet()

    # 3. Lógica del Encabezado (Membrete y Logo)
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
    elementos.append(Spacer(1, 0.2*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.8*inch, width=0.8*inch, height=0.8*inch, mask='auto')
        # Agregar marca de agua
        draw_watermark(canvas, doc)

    # 4. Título del Reporte
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)

    # Información adicional del reporte
    info_reporte = []
    if fecha_desde != 'N/A' and fecha_hasta != 'N/A':
        info_reporte.append(f"Período: Desde {fecha_desde} Hasta {fecha_hasta}")
    info_reporte.append(f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    for info in info_reporte:
        info_paragraph = Paragraph(info, styles['Normal'])
        info_paragraph.style.alignment = 1
        elementos.append(info_paragraph)
    
    elementos.append(Spacer(1, 0.3*inch))

    # 5. Lógica de la Tabla de Datos - Columnas específicas para inventario
    columnas = ['N°', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'MARCA', 'MODELO', 'SERIAL', 'UNIDAD ASIGNADA', 'ESTADO', 'VALOR (Bs.)']
    
    # Estilo para celdas de la tabla
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 7
    cell_style.leading = 8
    cell_style.wordWrap = 'LTR'
    
    # Estilo para encabezados de la tabla
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 7
    header_style.leading = 8
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    
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
            Paragraph(str(bien.get_estado_bien_display()), cell_style),
            Paragraph(f"{bien.valor_unitario_bs:,.2f}", cell_style),
        ])

    # Ajustar los anchos de columna para inventario general
    tabla_bienes = Table(
        datos_tabla,
        colWidths=[0.4*inch, 1.0*inch, 1.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 1.0*inch, 0.6*inch, 0.8*inch]
    )
    tabla_bienes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),  # Azul para encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Sin ROWBACKGROUNDS para que las filas sean transparentes
    ]))
    elementos.append(tabla_bienes)
    elementos.append(Spacer(1, 0.3*inch))

    # 6. Resumen estadístico
    if bienes_queryset.count() > 0:
        total_valor = sum(bien.valor_unitario_bs for bien in bienes_queryset)
        estados_count = {}
        for bien in bienes_queryset:
            estado = bien.get_estado_bien_display()
            estados_count[estado] = estados_count.get(estado, 0) + 1
        
        resumen_text = f"""
        <b>RESUMEN ESTADÍSTICO:</b><br/>
        • Total de Bienes: {bienes_queryset.count()}<br/>
        • Valor Total: Bs. {total_valor:,.2f}<br/>
        • Distribución por Estado: {', '.join([f'{estado}: {count}' for estado, count in estados_count.items()])}
        """
        resumen_paragraph = Paragraph(resumen_text, styles['Normal'])
        elementos.append(resumen_paragraph)
        elementos.append(Spacer(1, 0.3*inch))

    # 7. Lógica del Pie de Página (Firma)
    elementos.append(Spacer(1, 1.5*inch))

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

    # 8. Devolver el buffer con el PDF generado
    buffer.seek(0)
    return buffer

def generar_reporte_desincorporados_pdf(movimientos_queryset, fecha_desde, fecha_hasta, titulo_reporte):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
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
        'DIRECCIÓN GENERAL DE EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.2*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.8*inch, width=0.8*inch, height=0.8*inch, mask='auto')
        # Agregar marca de agua
        draw_watermark(canvas, doc)

    # Título del Reporte
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)

    # Información específica de desincorporaciones
    info_reporte = []
    info_reporte.append(f"Período: Desde {fecha_desde} Hasta {fecha_hasta}")
    info_reporte.append(f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    for info in info_reporte:
        info_paragraph = Paragraph(info, styles['Normal'])
        info_paragraph.style.alignment = 1
        elementos.append(info_paragraph)
    
    elementos.append(Spacer(1, 0.3*inch))

    # Tabla de Datos - Columnas específicas para desincorporaciones
    columnas = ['N°', 'FECHA DESINC.', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'CATEGORÍA', 'VALOR ORIGINAL (Bs.)', 'MOTIVO DESINCORPORACIÓN']
    
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 7
    cell_style.leading = 8
    cell_style.wordWrap = 'LTR'
    
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 7
    header_style.leading = 8
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    
    columnas_paragraph = [
        Paragraph(f'<font color="white"><b>{col}</b></font>', header_style) for col in columnas
    ]
    datos_tabla = [columnas_paragraph]
    
    for i, movimiento in enumerate(movimientos_queryset):
        categoria_nombre = movimiento.bien.categoria.nombre if movimiento.bien.categoria else 'N/A'
        datos_tabla.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(movimiento.fecha_movimiento.strftime('%d/%m/%Y'), cell_style),
            Paragraph(str(movimiento.bien.codigo_patrimonial), cell_style),
            Paragraph(str(movimiento.bien.descripcion), cell_style),
            Paragraph(str(categoria_nombre), cell_style),
            Paragraph(f"{movimiento.bien.valor_unitario_bs:,.2f}", cell_style),
            Paragraph(str(movimiento.motivo_desincorporacion or 'No especificado'), cell_style),
        ])

    tabla_reporte = Table(
        datos_tabla,
        colWidths=[0.4*inch, 0.8*inch, 1.0*inch, 1.8*inch, 0.8*inch, 1.0*inch, 1.2*inch]
    )
    tabla_reporte.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC143C')),  # Rojo para desincorporaciones
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Sin ROWBACKGROUNDS para que las filas sean transparentes
    ]))
    elementos.append(tabla_reporte)
    elementos.append(Spacer(1, 0.3*inch))

    # Resumen específico de desincorporaciones
    if movimientos_queryset.count() > 0:
        total_valor = sum(movimiento.bien.valor_unitario_bs for movimiento in movimientos_queryset)
        categorias_count = {}
        motivos_count = {}
        
        for movimiento in movimientos_queryset:
            categoria = movimiento.bien.categoria.nombre if movimiento.bien.categoria else 'Sin Categoría'
            categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
            
            motivo = movimiento.motivo_desincorporacion or 'No especificado'
            motivos_count[motivo] = motivos_count.get(motivo, 0) + 1
        
        resumen_text = f"""
        <b>RESUMEN DE DESINCORPORACIONES:</b><br/>
        • Total de Bienes Desincorporados: {movimientos_queryset.count()}<br/>
        • Valor Total Desincorporado: Bs. {total_valor:,.2f}<br/>
        • Distribución por Categoría: {', '.join([f'{categoria}: {count}' for categoria, count in list(categorias_count.items())[:3]])}<br/>
        • Principales Motivos: {', '.join([f'{motivo}: {count}' for motivo, count in list(motivos_count.items())[:3]])}
        """
        resumen_paragraph = Paragraph(resumen_text, styles['Normal'])
        elementos.append(resumen_paragraph)
        elementos.append(Spacer(1, 0.3*inch))

    # Pie de página (Firma)
    elementos.append(Spacer(1, 1.5*inch))
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
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
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
        'DIRECCIÓN GENERAL DE EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.2*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.8*inch, width=0.8*inch, height=0.8*inch, mask='auto')
        # Agregar marca de agua
        draw_watermark(canvas, doc)

    # Título del Reporte
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)

    # Información específica de traslados
    info_reporte = []
    info_reporte.append(f"Período: Desde {fecha_desde} Hasta {fecha_hasta}")
    info_reporte.append(f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    for info in info_reporte:
        info_paragraph = Paragraph(info, styles['Normal'])
        info_paragraph.style.alignment = 1
        elementos.append(info_paragraph)
    
    elementos.append(Spacer(1, 0.3*inch))

    # Tabla de Datos - Columnas específicas para traslados
    columnas = ['N°', 'FECHA TRASLADO', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'UNIDAD ORIGEN', 'UNIDAD DESTINO', 'RESPONSABLE', 'N° OFICIO']
    
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 7
    cell_style.leading = 8
    cell_style.wordWrap = 'LTR'
    
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 7
    header_style.leading = 8
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    
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
            Paragraph(str(movimiento.responsable_nuevo_nombre or 'No especificado'), cell_style),
            Paragraph(str(movimiento.numero_oficio_referencia or 'N/A'), cell_style)
        ])

    tabla_reporte = Table(
        datos_tabla,
        colWidths=[0.4*inch, 0.8*inch, 1.0*inch, 1.5*inch, 1.0*inch, 1.0*inch, 1.0*inch, 0.8*inch]
    )
    tabla_reporte.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8C00')),  # Naranja para traslados
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Sin ROWBACKGROUNDS para que las filas sean transparentes
    ]))
    elementos.append(tabla_reporte)
    elementos.append(Spacer(1, 0.3*inch))

    # Resumen específico de traslados
    if movimientos_queryset.count() > 0:
        unidades_origen_count = {}
        unidades_destino_count = {}
        responsables_count = {}
        
        for movimiento in movimientos_queryset:
            origen = movimiento.unidad_origen.nombre if movimiento.unidad_origen else 'Sin Origen'
            unidades_origen_count[origen] = unidades_origen_count.get(origen, 0) + 1
            
            destino = movimiento.unidad_destino.nombre if movimiento.unidad_destino else 'Sin Destino'
            unidades_destino_count[destino] = unidades_destino_count.get(destino, 0) + 1
            
            responsable = movimiento.responsable_nuevo_nombre or 'No especificado'
            responsables_count[responsable] = responsables_count.get(responsable, 0) + 1
        
        resumen_text = f"""
        <b>RESUMEN DE TRASLADOS:</b><br/>
        • Total de Traslados: {movimientos_queryset.count()}<br/>
        • Principales Unidades Origen: {', '.join([f'{origen}: {count}' for origen, count in list(unidades_origen_count.items())[:3]])}<br/>
        • Principales Unidades Destino: {', '.join([f'{destino}: {count}' for destino, count in list(unidades_destino_count.items())[:3]])}<br/>
        • Principales Responsables: {', '.join([f'{responsable}: {count}' for responsable, count in list(responsables_count.items())[:3]])}
        """
        resumen_paragraph = Paragraph(resumen_text, styles['Normal'])
        elementos.append(resumen_paragraph)
        elementos.append(Spacer(1, 0.3*inch))

    # Pie de página (Firma)
    elementos.append(Spacer(1, 1.5*inch))
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
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
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
    elementos.append(Spacer(1, 0.2*inch))
    
    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.8*inch, width=0.8*inch, height=0.8*inch, mask='auto')
        # Agregar marca de agua
        draw_watermark(canvas, doc)
    
    # Título y Fecha
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)
    
    # Información específica de depreciación
    info_reporte = []
    info_reporte.append(f"Cálculos hasta la fecha: {fecha_hasta}")
    info_reporte.append(f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    for info in info_reporte:
        info_paragraph = Paragraph(info, styles['Normal'])
        info_paragraph.style.alignment = 1
        elementos.append(info_paragraph)
    
    elementos.append(Spacer(1, 0.3*inch))
    
    # Tabla de Datos - Columnas específicas para depreciación
    columnas = ['N°', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'CATEGORÍA', 'VALOR ORIGINAL (Bs.)', 'DEPRECIACIÓN ACUMULADA (Bs.)', 'VALOR NETO EN LIBROS (Bs.)', '% DEPRECIACIÓN']
    
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 7
    cell_style.leading = 8
    cell_style.wordWrap = 'LTR'
    
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 7
    header_style.leading = 8
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    
    columnas_paragraph = [
        Paragraph(f'<font color="white"><b>{col}</b></font>', header_style) for col in columnas
    ]
    datos_tabla = [columnas_paragraph]
    
    for i, bien in enumerate(bienes_con_depreciacion):
        depreciacion_acumulada = bien.ultima_depreciacion_acumulada or 0
        valor_neto = bien.ultimo_valor_neto or bien.valor_unitario_bs
        porcentaje_depreciacion = (depreciacion_acumulada / bien.valor_unitario_bs * 100) if bien.valor_unitario_bs > 0 else 0
        categoria_nombre = bien.categoria.nombre if bien.categoria else 'N/A'
        
        datos_tabla.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(str(bien.codigo_patrimonial), cell_style),
            Paragraph(str(bien.descripcion), cell_style),
            Paragraph(str(categoria_nombre), cell_style),
            Paragraph(f"{bien.valor_unitario_bs:,.2f}", cell_style),
            Paragraph(f"{depreciacion_acumulada:,.2f}", cell_style),
            Paragraph(f"{valor_neto:,.2f}", cell_style),
            Paragraph(f"{porcentaje_depreciacion:.1f}%", cell_style)
        ])

    tabla_reporte = Table(
        datos_tabla,
        colWidths=[0.3*inch, 0.8*inch, 1.2*inch, 0.8*inch, 1.0*inch, 1.0*inch, 1.0*inch, 0.6*inch]
    )
    tabla_reporte.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4169E1')),  # Azul para depreciación
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Sin ROWBACKGROUNDS para que las filas sean transparentes
    ]))
    elementos.append(tabla_reporte)
    elementos.append(Spacer(1, 0.3*inch))

    # Resumen específico de depreciación
    if bienes_con_depreciacion.count() > 0:
        total_valor_original = sum(bien.valor_unitario_bs for bien in bienes_con_depreciacion)
        total_depreciacion_acumulada = sum(bien.ultima_depreciacion_acumulada or 0 for bien in bienes_con_depreciacion)
        total_valor_neto = sum(bien.ultimo_valor_neto or bien.valor_unitario_bs for bien in bienes_con_depreciacion)
        porcentaje_total_depreciacion = (total_depreciacion_acumulada / total_valor_original * 100) if total_valor_original > 0 else 0
        
        categorias_count = {}
        for bien in bienes_con_depreciacion:
            categoria = bien.categoria.nombre if bien.categoria else 'Sin Categoría'
            categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
        
        resumen_text = f"""
        <b>RESUMEN DE DEPRECIACIÓN ACUMULADA:</b><br/>
        • Total de Bienes: {bienes_con_depreciacion.count()}<br/>
        • Valor Original Total: Bs. {total_valor_original:,.2f}<br/>
        • Depreciación Acumulada Total: Bs. {total_depreciacion_acumulada:,.2f}<br/>
        • Valor Neto Total: Bs. {total_valor_neto:,.2f}<br/>
        • Porcentaje Promedio de Depreciación: {porcentaje_total_depreciacion:.1f}%<br/>
        • Distribución por Categoría: {', '.join([f'{categoria}: {count}' for categoria, count in list(categorias_count.items())[:3]])}
        """
        resumen_paragraph = Paragraph(resumen_text, styles['Normal'])
        elementos.append(resumen_paragraph)
        elementos.append(Spacer(1, 0.3*inch))

    # Pie de página (Firma)
    elementos.append(Spacer(1, 1.5*inch))
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

def generar_reporte_por_categoria_pdf(bienes_queryset, categoria_nombre, fecha_desde, fecha_hasta, titulo_reporte=None):
    """Función específica para reporte por categoría con formato optimizado"""
    if titulo_reporte is None:
        titulo_reporte = f"INVENTARIO DE BIENES - CATEGORÍA: {categoria_nombre.upper()}"
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
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
        'DIRECCIÓN GENERAL DE EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.2*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.8*inch, width=0.8*inch, height=0.8*inch, mask='auto')
        # Agregar marca de agua
        draw_watermark(canvas, doc)

    # Título del Reporte
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)

    # Información específica de la categoría
    info_reporte = []
    info_reporte.append(f"Categoría: {categoria_nombre}")
    if fecha_desde != 'N/A' and fecha_hasta != 'N/A':
        info_reporte.append(f"Período: Desde {fecha_desde} Hasta {fecha_hasta}")
    info_reporte.append(f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    for info in info_reporte:
        info_paragraph = Paragraph(info, styles['Normal'])
        info_paragraph.style.alignment = 1
        elementos.append(info_paragraph)
    
    elementos.append(Spacer(1, 0.3*inch))

    # Tabla de Datos - Columnas específicas para categoría
    columnas = ['N°', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'MARCA', 'MODELO', 'SERIAL', 'UNIDAD ASIGNADA', 'ESTADO', 'VALOR (Bs.)']
    
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 7
    cell_style.leading = 8
    cell_style.wordWrap = 'LTR'
    
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 7
    header_style.leading = 8
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    
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
            Paragraph(str(bien.get_estado_bien_display()), cell_style),
            Paragraph(f"{bien.valor_unitario_bs:,.2f}", cell_style),
        ])

    tabla_bienes = Table(
        datos_tabla,
        colWidths=[0.4*inch, 1.0*inch, 1.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 1.0*inch, 0.6*inch, 0.8*inch]
    )
    tabla_bienes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),  # Verde para categorías
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Sin ROWBACKGROUNDS para que las filas sean transparentes
    ]))
    elementos.append(tabla_bienes)
    elementos.append(Spacer(1, 0.3*inch))

    # Resumen específico de la categoría
    if bienes_queryset.count() > 0:
        total_valor = sum(bien.valor_unitario_bs for bien in bienes_queryset)
        estados_count = {}
        unidades_count = {}
        for bien in bienes_queryset:
            estado = bien.get_estado_bien_display()
            estados_count[estado] = estados_count.get(estado, 0) + 1
            
            unidad = bien.unidad_administrativa_actual.nombre if bien.unidad_administrativa_actual else 'Sin Asignar'
            unidades_count[unidad] = unidades_count.get(unidad, 0) + 1
        
        resumen_text = f"""
        <b>RESUMEN DE LA CATEGORÍA "{categoria_nombre.upper()}":</b><br/>
        • Total de Bienes: {bienes_queryset.count()}<br/>
        • Valor Total: Bs. {total_valor:,.2f}<br/>
        • Distribución por Estado: {', '.join([f'{estado}: {count}' for estado, count in estados_count.items()])}<br/>
        • Distribución por Unidad: {', '.join([f'{unidad}: {count}' for unidad, count in list(unidades_count.items())[:3]])}
        """
        resumen_paragraph = Paragraph(resumen_text, styles['Normal'])
        elementos.append(resumen_paragraph)
        elementos.append(Spacer(1, 0.3*inch))

    # Pie de página (Firma)
    elementos.append(Spacer(1, 1.5*inch))
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

    doc.build(elementos, onFirstPage=draw_logo)
    buffer.seek(0)
    return buffer

def generar_reporte_por_unidad_pdf(bienes_queryset, unidad_nombre, fecha_desde, fecha_hasta, titulo_reporte=None):
    """Función específica para reporte por unidad administrativa con formato optimizado"""
    if titulo_reporte is None:
        titulo_reporte = f"INVENTARIO DE BIENES - UNIDAD: {unidad_nombre.upper()}"
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
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
        'DIRECCIÓN GENERAL DE EMPRESAS Y SERVICIOS<br/>'
        'INSTITUTO DE PREVISIÓN SOCIAL DE LA FUERZA ARMADA NACIONAL BOLIVARIANA<br/>'
        'GERENCIA DE FINANZAS<br/>'
        'UNIDAD DE BIENES PÚBLICOS'
    )
    membrete_paragraph = Paragraph(membrete_text, styles['Normal'])
    elementos.append(membrete_paragraph)
    elementos.append(Spacer(1, 0.2*inch))

    def draw_logo(canvas, doc):
        if logo:
            canvas.drawImage(logo, doc.leftMargin, doc.height + doc.topMargin - 0.8*inch, width=0.8*inch, height=0.8*inch, mask='auto')
        # Agregar marca de agua
        draw_watermark(canvas, doc)

    # Título del Reporte
    titulo = Paragraph(titulo_reporte, styles['h2'])
    titulo.style.alignment = 1
    elementos.append(titulo)

    # Información específica de la unidad
    info_reporte = []
    info_reporte.append(f"Unidad Administrativa: {unidad_nombre}")
    if fecha_desde != 'N/A' and fecha_hasta != 'N/A':
        info_reporte.append(f"Período: Desde {fecha_desde} Hasta {fecha_hasta}")
    info_reporte.append(f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    for info in info_reporte:
        info_paragraph = Paragraph(info, styles['Normal'])
        info_paragraph.style.alignment = 1
        elementos.append(info_paragraph)
    
    elementos.append(Spacer(1, 0.3*inch))

    # Tabla de Datos - Columnas específicas para unidad
    columnas = ['N°', 'CÓDIGO PATRIMONIAL', 'DESCRIPCIÓN', 'CATEGORÍA', 'MARCA', 'MODELO', 'SERIAL', 'ESTADO', 'VALOR (Bs.)']
    
    cell_style = styles['Normal'].clone('cell_style')
    cell_style.fontSize = 7
    cell_style.leading = 8
    cell_style.wordWrap = 'LTR'
    
    header_style = styles['Normal'].clone('header_style')
    header_style.fontSize = 7
    header_style.leading = 8
    header_style.wordWrap = 'LTR'
    header_style.alignment = 1
    
    columnas_paragraph = [
        Paragraph(f'<font color="white"><b>{col}</b></font>', header_style) for col in columnas
    ]
    datos_tabla = [columnas_paragraph]
    
    for i, bien in enumerate(bienes_queryset):
        categoria_nombre = bien.categoria.nombre if bien.categoria else 'N/A'
        datos_tabla.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(str(bien.codigo_patrimonial), cell_style),
            Paragraph(str(bien.descripcion), cell_style),
            Paragraph(str(categoria_nombre), cell_style),
            Paragraph(str(bien.marca or ''), cell_style),
            Paragraph(str(bien.modelo or ''), cell_style),
            Paragraph(str(bien.serial or ''), cell_style),
            Paragraph(str(bien.get_estado_bien_display()), cell_style),
            Paragraph(f"{bien.valor_unitario_bs:,.2f}", cell_style),
        ])

    tabla_bienes = Table(
        datos_tabla,
        colWidths=[0.4*inch, 1.0*inch, 1.3*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.8*inch, 0.6*inch, 0.8*inch]
    )
    tabla_bienes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B4513')),  # Marrón para unidades
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Sin ROWBACKGROUNDS para que las filas sean transparentes
    ]))
    elementos.append(tabla_bienes)
    elementos.append(Spacer(1, 0.3*inch))

    # Resumen específico de la unidad
    if bienes_queryset.count() > 0:
        total_valor = sum(bien.valor_unitario_bs for bien in bienes_queryset)
        estados_count = {}
        categorias_count = {}
        for bien in bienes_queryset:
            estado = bien.get_estado_bien_display()
            estados_count[estado] = estados_count.get(estado, 0) + 1
            
            categoria = bien.categoria.nombre if bien.categoria else 'Sin Categoría'
            categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
        
        resumen_text = f"""
        <b>RESUMEN DE LA UNIDAD "{unidad_nombre.upper()}":</b><br/>
        • Total de Bienes Asignados: {bienes_queryset.count()}<br/>
        • Valor Total: Bs. {total_valor:,.2f}<br/>
        • Distribución por Estado: {', '.join([f'{estado}: {count}' for estado, count in estados_count.items()])}<br/>
        • Distribución por Categoría: {', '.join([f'{categoria}: {count}' for categoria, count in list(categorias_count.items())[:3]])}
        """
        resumen_paragraph = Paragraph(resumen_text, styles['Normal'])
        elementos.append(resumen_paragraph)
        elementos.append(Spacer(1, 0.3*inch))

    # Pie de página (Firma)
    elementos.append(Spacer(1, 1.5*inch))
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

    doc.build(elementos, onFirstPage=draw_logo)
    buffer.seek(0)
    return buffer