from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Max, F, Subquery, OuterRef, Q
from django.db import transaction
import pandas as pd
from .models import Bien, MovimientoBien, DepreciacionMensual, Categoria
from .serializers import BienSerializer, MovimientoBienSerializer, CategoriaSerializer
from django.utils import timezone
from unidades_administrativas_app.models import UnidadAdministrativa
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import qrcode
from io import BytesIO
from decimal import Decimal
from .pdf_generator import generar_reporte_inventario_pdf, generar_reporte_desincorporados_pdf, generar_reporte_traslados_pdf
from .excel_generator import generar_reporte_inventario_excel, generar_reporte_desincorporados_excel, generar_reporte_traslados_excel

# from unidades_administrativas_app.models import UnidadAdministrativa # Si necesitas la instancia, ya está importada en serializers.py y accesible a través del movimiento

class BienViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver, crear, editar y eliminar Bienes.
    """
    queryset = Bien.objects.all().order_by('-fecha_creacion') # Obtiene todos los Bienes, ordenados
    serializer_class = BienSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

class MovimientoBienViewSet(viewsets.ModelViewSet):
    """
    API endpoint para registrar y ver movimientos de bienes.
    Al crear un movimiento de TRASLADO o DESINCORPORACION,
    se actualiza el bien correspondiente.
    """
    queryset = MovimientoBien.objects.all().select_related(
        'bien', 'unidad_origen', 'unidad_destino', 'usuario_registra'
    ).order_by('-fecha_movimiento')
    serializer_class = MovimientoBienSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados

    def perform_create(self, serializer):
        movimiento = serializer.save(usuario_registra=self.request.user if self.request.user.is_authenticated else None)
        bien_afectado = movimiento.bien

        if movimiento.tipo_movimiento == 'TRASLADO':
            if movimiento.unidad_destino:
                # Asumiendo que tienes este campo en Bien (lo añadiremos después)
                bien_afectado.unidad_administrativa_actual = movimiento.unidad_destino 
            if movimiento.ubicacion_nueva_especifica:
                bien_afectado.ubicacion_fisica_especifica = movimiento.ubicacion_nueva_especifica
            if movimiento.responsable_nuevo_nombre:
                bien_afectado.responsable_asignado_nombre = movimiento.responsable_nuevo_nombre
            bien_afectado.fecha_actualizacion = timezone.now()
            bien_afectado.save()
            print(f"Bien {bien_afectado.id} actualizado por traslado.")

        elif movimiento.tipo_movimiento == 'DESINCORPORACION':
            bien_afectado.estado_bien = 'DESINCORPORADO'
            # Podrías limpiar campos como responsable o ubicación aquí, si es necesario
            # bien_afectado.responsable_asignado_nombre = None 
            # bien_afectado.unidad_administrativa_actual = None 
            bien_afectado.fecha_actualizacion = timezone.now()
            bien_afectado.save()
            print(f"Bien {bien_afectado.id} desincorporado.")

        elif movimiento.tipo_movimiento == 'INCORPORACION':
            # Si el bien estaba desincorporado, se actualiza su estado.
            # También se puede usar para asignar/actualizar detalles iniciales.
            if bien_afectado.estado_bien == 'DESINCORPORADO' or not bien_afectado.estado_bien:
                bien_afectado.estado_bien = 'NUEVO' # O un estado más apropiado según la lógica de negocio
            
            if movimiento.unidad_destino: # Asigna la unidad del movimiento como la actual del bien
                bien_afectado.unidad_administrativa_actual = movimiento.unidad_destino
            if movimiento.ubicacion_nueva_especifica:
                bien_afectado.ubicacion_fisica_especifica = movimiento.ubicacion_nueva_especifica
            if movimiento.responsable_nuevo_nombre:
                bien_afectado.responsable_asignado_nombre = movimiento.responsable_nuevo_nombre
            
            bien_afectado.fecha_actualizacion = timezone.now()
            bien_afectado.save()
            print(f"Bien {bien_afectado.id} actualizado por incorporación.")


class DashboardStatsView(APIView):
    """
    Vista para obtener estadísticas agregadas para el Dashboard principal.
    """
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden ver el dashboard

    def get(self, request, format=None):
        # 1. Valor Patrimonial Total (Suma de valor_unitario_bs de todos los bienes)
        valor_patrimonial = Bien.objects.aggregate(
            total=Sum('valor_unitario_bs')
        )['total'] or 0

        # 2. Depreciación Acumulada (LÓGICA ACTUALIZADA)
        subquery = DepreciacionMensual.objects.filter(
            bien=OuterRef('pk')
        ).order_by('-anio', '-mes').values('depreciacion_acumulada')[:1]
        depreciacion_acumulada_total = Bien.objects.annotate(
            ultima_dep_acumulada=Subquery(subquery)
        ).aggregate(
            total_depreciacion=Sum('ultima_dep_acumulada')
        )['total_depreciacion'] or 0

        # 3. Conteo de Bienes Obsoletos (sin cambios)
        bienes_obsoletos_count = Bien.objects.filter(estado_bien='OBSOLETO').count()

        # 4. Conteo Total de Sedes/Unidades Activas (sin cambios)
        unidades_activas_count = UnidadAdministrativa.objects.filter(activa=True).count()

        # 5. Distribución de Bienes por Estado
        distribucion_por_estado = Bien.objects.values('estado_bien').annotate(
            count=Count('id')
        ).order_by('estado_bien')

        # 6. Inventario por Sede/Unidad Administrativa
        inventario_por_sede = UnidadAdministrativa.objects.filter(activa=True).annotate(
            cantidad_bienes=Count('bienes_asignados'),
            valor_estimado=Sum('bienes_asignados__valor_unitario_bs')
        ).values('nombre', 'cantidad_bienes', 'valor_estimado').order_by('-cantidad_bienes')

        stats = {
            'valor_patrimonial_total': valor_patrimonial,
            'depreciacion_acumulada': depreciacion_acumulada_total,
            'bienes_obsoletos_count': bienes_obsoletos_count,
            'unidades_activas_count': unidades_activas_count,
            'distribucion_por_estado': list(distribucion_por_estado),
            'inventario_por_sede': list(inventario_por_sede)
        }
        return Response(stats)

class BienesUploadView(APIView):
    """
    Vista para manejar la carga masiva de bienes desde un archivo CSV o Excel.
    """
    permission_classes = [permissions.IsAdminUser] # Solo administradores pueden hacer cargas masivas

    def post(self, request, *args, **kwargs):
        archivo = request.FILES.get('file')

        if not archivo:
            return Response({'error': 'No se proporcionó ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        # Determinar el tipo de archivo y leerlo con pandas
        try:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo, sep=';', encoding='utf-8')
            elif archivo.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(archivo)
            else:
                return Response({'error': 'Formato de archivo no soportado.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error al leer el archivo: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        # Mapeo de columnas del archivo Excel/CSV a los campos del modelo Django
        column_map = {
            'FECHA DE ADQUISICIÓN': 'fecha_adquisicion',
            'DESCRIPCIÓN': 'descripcion',
            'CANTIDAD': 'cantidad',
            'MARCA': 'marca',
            'MODELO': 'modelo',
            'SERIAL': 'serial',
            'CÓDIGO': 'codigo_anterior',
            'N° ORDEN DE COMPRA O N° DE FACTURA': 'n_orden_compra_factura',
            'PROVEEDOR': 'nombre_proveedor',
            'VALOR UNITARIO Bs.': 'valor_unitario_bs',
            'VALOR UNITARIO $': 'valor_unitario_usd',
            'RESPONSABLE DEL ÁREA': 'responsable_asignado_nombre',
            'CARGO DEL RESPONSABLE': 'responsable_asignado_cargo',
            'UBICACIÓN FÍSICA': 'ubicacion_fisica_especifica',
            'ESTADO DEL BIEN': 'estado_bien',
            'OBSERVACIONES': 'observaciones'
        }

        df.rename(columns=column_map, inplace=True)

        # Convertir la columna de estado a los valores internos del modelo (ej: 'Nuevo' -> 'NUEVO')
        estado_map = {
            'Nuevo': 'NUEVO',
            'Bueno': 'BUENO',
            'Regular': 'REGULAR',
            'Malo': 'MALO',
            'En Reparación': 'EN_REPARACION',
            'Obsoleto': 'OBSOLETO',
            'Desincorporado': 'DESINCORPORADO'
        }
        if 'estado_bien' in df.columns:
            df['estado_bien'] = df['estado_bien'].map(estado_map).fillna('NUEVO')

        bienes_a_crear = df.to_dict('records')
        errors = []
        success_count = 0

        try:
            with transaction.atomic(): # Usar una transacción atómica
                for i, record in enumerate(bienes_a_crear):
                    # Limpiar datos: convertir NaN de pandas a None
                    cleaned_record = {k: v if pd.notna(v) else None for k, v in record.items()}

                    serializer = BienSerializer(data=cleaned_record)
                    if serializer.is_valid():
                        serializer.save()
                        success_count += 1
                    else:
                        errors.append({'fila': i + 2, 'errores': serializer.errors})
                
                # Si hay algún error, revertir toda la transacción
                if errors:
                    raise Exception("Errores de validación encontrados durante la carga.")

        except Exception as e:
            # Si la excepción fue la que lanzamos, devolvemos los errores de validación
            if str(e) == "Errores de validación encontrados durante la carga.":
                 return Response({
                    'status': 'Error de validación',
                    'success_count': success_count,
                    'error_count': len(errors),
                    'errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)
            # Para otros errores inesperados
            return Response({'error': f'Error inesperado en la transacción: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status': 'Carga masiva completada exitosamente',
            'total_procesados': len(bienes_a_crear),
            'bienes_creados': success_count
        }, status=status.HTTP_201_CREATED)

class GenerarQRBienView(APIView):
    """
    Vista para generar y descargar el código QR de un bien específico.
    """
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden generar QR

    def get(self, request, bien_id, format=None):
        bien = get_object_or_404(Bien, id=bien_id)

        # Datos a incluir en el QR: aquí puedes personalizar qué datos incluir
        qr_data = f"Bien ID: {bien.id}\nDescripción: {bien.descripcion}\nEstado: {bien.estado_bien}"
        
        # Generar el código QR
        qr_img = qrcode.make(qr_data)

        # Guardar la imagen en un buffer en memoria
        buf = BytesIO()
        qr_img.save(buf, format='PNG')
        buf.seek(0)

        # Devolver la imagen como respuesta HTTP
        return HttpResponse(buf.getvalue(), content_type='image/png')

        # También podrías devolver un archivo para descargar, usando:
        # response = HttpResponse(content_type='image/png')
        # response['Content-Disposition'] = f'attachment; filename="qr_bien_{bien_id}.png"'
        # response.write(buf.getvalue())
        # return response

class BienQRCodeView(APIView):
    """
    Genera y devuelve una imagen de código QR para un bien específico.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        bien = get_object_or_404(Bien, pk=pk)
        qr_data = f"http://localhost:8080/bienes/detalle/{bien.id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer, content_type="image/png")
    
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class CalcularDepreciacionView(APIView):
    """
    Vista para iniciar el proceso de cálculo de depreciación para un período específico (mes/año).
    """
    permission_classes = [permissions.IsAdminUser] # Solo administradores pueden ejecutar este proceso

    def post(self, request, *args, **kwargs):
        mes = request.data.get('mes')
        anio = request.data.get('anio')

        if not mes or not anio:
            return Response({'error': 'Mes y año son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mes = int(mes)
            anio = int(anio)
            if not (1 <= mes <= 12 and anio > 2000):
                raise ValueError()
        except (ValueError, TypeError):
            return Response({'error': 'Mes o año inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        bienes_a_depreciar = Bien.objects.filter(
            vida_util_estimada_anios__isnull=False,
            vida_util_estimada_anios__gt=0,
            metodo_depreciacion__isnull=False,
            estado_bien__in=['NUEVO', 'BUENO', 'REGULAR', 'EN_REPARACION']
        )

        bienes_calculados = 0
        bienes_omitidos = 0
        errores = []

        with transaction.atomic():
            for bien in bienes_a_depreciar:
                if DepreciacionMensual.objects.filter(bien=bien, mes=mes, anio=anio).exists():
                    bienes_omitidos += 1
                    continue

                ultimo_calculo = DepreciacionMensual.objects.filter(bien=bien).order_by('-anio', '-mes').first()
                valor_en_libros_actual = ultimo_calculo.valor_neto_en_libros if ultimo_calculo else bien.valor_unitario_bs

                if valor_en_libros_actual <= bien.valor_residual:
                    bienes_omitidos += 1
                    continue

                depreciacion_del_mes = Decimal('0.00')

                if bien.metodo_depreciacion == 'LINEA_RECTA':
                    vida_util_meses = bien.vida_util_estimada_anios * 12
                    base_depreciable = bien.valor_unitario_bs - bien.valor_residual
                    if vida_util_meses > 0:
                        depreciacion_del_mes = base_depreciable / Decimal(vida_util_meses)

                elif bien.metodo_depreciacion == 'SALDO_DECRECIENTE':
                    tasa_depreciacion_anual = (Decimal('1') / Decimal(bien.vida_util_estimada_anios)) * 2
                    depreciacion_del_mes = (valor_en_libros_actual * tasa_depreciacion_anual) / Decimal('12')

                if (valor_en_libros_actual - depreciacion_del_mes) < bien.valor_residual:
                    depreciacion_del_mes = valor_en_libros_actual - bien.valor_residual

                depreciacion_acumulada_anterior = ultimo_calculo.depreciacion_acumulada if ultimo_calculo else Decimal('0.00')
                nueva_depreciacion_acumulada = depreciacion_acumulada_anterior + depreciacion_del_mes
                nuevo_valor_neto_en_libros = bien.valor_unitario_bs - nueva_depreciacion_acumulada

                DepreciacionMensual.objects.create(
                    bien=bien,
                    mes=mes,
                    anio=anio,
                    valor_depreciado_mes=depreciacion_del_mes,
                    depreciacion_acumulada=nueva_depreciacion_acumulada,
                    valor_neto_en_libros=nuevo_valor_neto_en_libros
                )
                bienes_calculados += 1

        return Response({
            'status': 'Cálculo de depreciación completado.',
            'mes': mes,
            'anio': anio,
            'bienes_calculados': bienes_calculados,
            'bienes_omitidos': bienes_omitidos,
            'errores': errores
        }, status=status.HTTP_200_OK)
    
class ReporteInventarioGeneralPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        fecha_desde = request.query_params.get('fecha_desde', 'N/A')
        fecha_hasta = request.query_params.get('fecha_hasta', 'N/A')

        bienes = Bien.objects.all().order_by('codigo_patrimonial')

        buffer = generar_reporte_inventario_pdf(bienes, fecha_desde, fecha_hasta)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_inventario_general.pdf"'

        return response
    
class ReporteInventarioGeneralExcel(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Aquí puedes añadir la misma lógica de filtrado que usarías para el PDF
        # Por ahora, obtenemos todos los bienes.
        bienes = Bien.objects.all().order_by('codigo_patrimonial')

        titulo = "INVENTARIO GENERAL DE BIENES PÚBLICOS"
        buffer = generar_reporte_inventario_excel(bienes, titulo)

        # Preparar la respuesta HTTP
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="reporte_inventario_general.xlsx"'

        return response
    
class ReporteBienesPorCategoriaPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Obtener el ID de la categoría desde los parámetros de la URL (ej: ?categoria_id=1)
        categoria_id = request.query_params.get('categoria_id')

        if not categoria_id:
            return Response({'error': 'Debe proporcionar un ID de categoría.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener la categoría y los bienes asociados
            categoria = Categoria.objects.get(pk=categoria_id)
            bienes = Bien.objects.filter(categoria=categoria).order_by('codigo_patrimonial')

            # Definir título y rango de fechas (puedes hacerlos dinámicos si los pasas como params)
            titulo = f"INVENTARIO DE BIENES - CATEGORÍA: {categoria.nombre.upper()}"
            fecha_desde = request.query_params.get('fecha_desde', 'N/A')
            fecha_hasta = request.query_params.get('fecha_hasta', 'N/A')

            # Llamar a la función que genera el PDF con los datos filtrados
            buffer = generar_reporte_inventario_pdf(bienes, fecha_desde, fecha_hasta, titulo)

            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_bienes_categoria_{categoria.nombre}.pdf"'
            return response

        except Categoria.DoesNotExist:
            return Response({'error': 'La categoría especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)


class ReporteBienesPorCategoriaExcel(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        categoria_id = request.query_params.get('categoria_id')
        if not categoria_id:
            return Response({'error': 'Debe proporcionar un ID de categoría.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            categoria = Categoria.objects.get(pk=categoria_id)
            bienes = Bien.objects.filter(categoria=categoria).order_by('codigo_patrimonial')

            titulo = f"Inventario de Bienes - Categoría: {categoria.nombre}"

            buffer = generar_reporte_inventario_excel(bienes, titulo)

            response = HttpResponse(
                buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="reporte_bienes_categoria_{categoria.nombre}.xlsx"'
            return response

        except Categoria.DoesNotExist:
            return Response({'error': 'La categoría especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)

class ReporteBienesPorUnidadPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unidad_id = request.query_params.get('unidad_id')
        if not unidad_id:
            return Response({'error': 'Debe proporcionar un ID de unidad.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            unidad = UnidadAdministrativa.objects.get(pk=unidad_id)
            bienes = Bien.objects.filter(unidad_administrativa_actual=unidad).order_by('codigo_patrimonial')
            titulo = f"INVENTARIO DE BIENES - UNIDAD: {unidad.nombre.upper()}"
            fecha_desde = request.query_params.get('fecha_desde', 'N/A')
            fecha_hasta = request.query_params.get('fecha_hasta', 'N/A')
            buffer = generar_reporte_inventario_pdf(bienes, fecha_desde, fecha_hasta, titulo)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_bienes_unidad_{unidad.nombre}.pdf"'
            return response
        except UnidadAdministrativa.DoesNotExist:
            return Response({'error': 'La unidad especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)

class ReporteBienesPorUnidadExcel(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unidad_id = request.query_params.get('unidad_id')
        if not unidad_id:
            return Response({'error': 'Debe proporcionar un ID de unidad.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            unidad = UnidadAdministrativa.objects.get(pk=unidad_id)
            bienes = Bien.objects.filter(unidad_administrativa_actual=unidad).order_by('codigo_patrimonial')
            titulo = f"Inventario de Bienes - Unidad: {unidad.nombre}"
            buffer = generar_reporte_inventario_excel(bienes, titulo)
            response = HttpResponse(
                buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="reporte_bienes_unidad_{unidad.nombre}.xlsx"'
            return response
        except UnidadAdministrativa.DoesNotExist:
            return Response({'error': 'La unidad especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)

class ReporteBienesDesincorporadosPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')

        if not fecha_desde or not fecha_hasta:
            return Response({'error': 'Debe proporcionar un rango de fechas (fecha_desde y fecha_hasta).'}, status=status.HTTP_400_BAD_REQUEST)

        # Filtrar los movimientos de desincorporación por rango de fechas
        movimientos = MovimientoBien.objects.filter(
            tipo_movimiento='DESINCORPORACION',
            fecha_movimiento__date__range=[fecha_desde, fecha_hasta]
        ).select_related('bien').order_by('fecha_movimiento')

        titulo = "RELACIÓN DE BIENES DESINCORPORADOS"
        buffer = generar_reporte_desincorporados_pdf(movimientos, fecha_desde, fecha_hasta, titulo)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_desincorporados.pdf"'
        return response

class ReporteBienesDesincorporadosExcel(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        if not fecha_desde or not fecha_hasta:
            return Response({'error': 'Debe proporcionar un rango de fechas.'}, status=status.HTTP_400_BAD_REQUEST)

        movimientos = MovimientoBien.objects.filter(
            tipo_movimiento='DESINCORPORACION',
            fecha_movimiento__date__range=[fecha_desde, fecha_hasta]
        ).select_related('bien').order_by('fecha_movimiento')

        titulo = "Relación de Bienes Desincorporados"
        buffer = generar_reporte_desincorporados_excel(movimientos, titulo)

        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_desincorporados.xlsx"'
        return response

class ReporteBienesTrasladadosPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        unidad_id = request.query_params.get('unidad_id') # Filtro opcional de unidad

        if not fecha_desde or not fecha_hasta:
            return Response({'error': 'Debe proporcionar un rango de fechas.'}, status=status.HTTP_400_BAD_REQUEST)

        movimientos = MovimientoBien.objects.filter(
            tipo_movimiento='TRASLADO',
            fecha_movimiento__date__range=[fecha_desde, fecha_hasta]
        ).select_related('bien', 'unidad_origen', 'unidad_destino').order_by('fecha_movimiento')

        # Si se proporciona una unidad, filtrar si es origen O destino
        if unidad_id:
            movimientos = movimientos.filter(Q(unidad_origen_id=unidad_id) | Q(unidad_destino_id=unidad_id))

        titulo = "RELACIÓN DE BIENES TRASLADADOS"
        buffer = generar_reporte_traslados_pdf(movimientos, fecha_desde, fecha_hasta, titulo)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_traslados.pdf"'
        return response

class ReporteBienesTrasladadosExcel(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        unidad_id = request.query_params.get('unidad_id') # Filtro opcional de unidad

        if not fecha_desde or not fecha_hasta:
            return Response({'error': 'Debe proporcionar un rango de fechas.'}, status=status.HTTP_400_BAD_REQUEST)

        movimientos = MovimientoBien.objects.filter(
            tipo_movimiento='TRASLADO',
            fecha_movimiento__date__range=[fecha_desde, fecha_hasta]
        ).select_related('bien', 'unidad_origen', 'unidad_destino').order_by('fecha_movimiento')

        # Si se proporciona una unidad, filtrar si es origen O destino
        if unidad_id:
            movimientos = movimientos.filter(Q(unidad_origen_id=unidad_id) | Q(unidad_destino_id=unidad_id))

        titulo = "Relación de Bienes Trasladados"
        buffer = generar_reporte_traslados_excel(movimientos, fecha_desde, fecha_hasta, titulo)

        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_traslados.xlsx"'
        return response
