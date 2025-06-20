from django.db import models
from django.contrib.auth.models import User
from products.models import ProductMaterial, Product, Material
from base.models import BaseModel
from django.utils.text import slugify


class ContadorProforma(models.Model):
    ultimo_numero = models.PositiveIntegerField(default=0)

#proforma 
class Proforma(BaseModel):
    proforma_num = models.CharField(max_length=100, unique=True, blank=True) #P0001
    estado = models.CharField(max_length=20, default='pendiente')  # pendiente, revisado, etc.
    fecha = models.DateField(auto_now_add=True)
    preciototal = models.DecimalField(max_digits=10, decimal_places=2, default=0) #se le suma si hay instalacion
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proformas') 
    pdf = models.FileField(upload_to='proformas_pdfs/', blank=True, null=True)
    
    @property
    def tiene_contrato(self):
        return self.contratos.exists()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.proforma_num)
        super(Proforma, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Proforma numero {self.proforma_num}'

class Cotizacion(models.Model):
    proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE, related_name='cotizaciones')
    producto = models.ForeignKey(ProductMaterial, on_delete=models.CASCADE, related_name='cotizaciones')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    alto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ancho = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    color = models.TextField(max_length=50, default="negro")
    chapa = models.TextField(max_length=50, default="chapa")
    pregunta_1 = models.TextField()
    pregunta_2 = models.TextField()
    pregunta_3 = models.TextField()
    #estado = models.CharField(max_length=20, default='pendiente')
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precioinstalacion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preciototal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Cotización agregada'
    
# contrato 
class Contrato(BaseModel):
    contrato_num = models.CharField(max_length=100) #C0001
    cantidad = models.PositiveIntegerField()
    preciototal = models.DecimalField(max_digits=10, decimal_places=2)
    acuenta = models.DecimalField(max_digits=10, decimal_places=2)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    fechaEntrega = models.DateField()
    estado_pedido = models.CharField(max_length=20, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('en_produccion', 'En Producción'),
        ('entregado', 'Entregado'),
        ('anulado', 'Anulado')
    ])
    detale_extra = models.TextField(max_length=250, default=" ") #se agrega algun detalle extra
    pdf = models.FileField(upload_to='contratos_pdfs/', blank=True, null=True)
    proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE, related_name="contratos", blank=True, null=True)

    @property
    def cliente(self):
        return self.proforma.cliente if self.proforma else None
    
    @property
    def estado_deuda(self):
        return 'pagado' if self.acuenta >= self.preciototal else 'debe'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.contrato_num)
        super(Contrato, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.contrato_num

class OpcionCotizacion(models.Model):
    cotizacion = models.ForeignKey('Cotizacion', on_delete=models.CASCADE, related_name='opciones')
    titulo = models.CharField(max_length=100)  # Ej: "Básico", "Full", "Premium"
    precio_instalacion = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion_adicional = models.TextField(blank=True)  # por si deseas dar detalles
    preciototal = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    precio_prediccion = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    precio_real = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.cotizacion}'

class OpcionContrato(models.Model):
    contrato = models.ForeignKey('Contrato', on_delete=models.CASCADE, related_name='opciones_elegidas')
    cotizacion = models.ForeignKey('Cotizacion', on_delete=models.CASCADE)
    opcion = models.ForeignKey('OpcionCotizacion', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.contrato.contrato_num} - {self.cotizacion.id} - {self.opcion.titulo}"
